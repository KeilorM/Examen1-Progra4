from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Usuario
import os
import httpx
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db

# ── Configuración JWT ──────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ── Generar token JWT ──────────────────────────────────────────────────────────
def crear_token(data: dict) -> str:
    """
    Recibe un dict (normalmente {"sub": email}) y devuelve el JWT firmado.
    """
    payload = data.copy()
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expira})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ── Verificar token JWT ────────────────────────────────────────────────────────
def verificar_token(token: str) -> dict:
    """
    Decodifica y valida el JWT. Lanza 401 si es inválido o expirado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: sin subject",
            )
        return {"email": email}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Login / registro con Google SSO ───────────────────────────────────────────
def login_o_registrar_usuario(db: Session, google_data: dict) -> dict:
    """
    Recibe los datos que llegan de Google (email, nombre, google_id).
    - Si el usuario ya existe → lo devuelve.
    - Si no existe → lo crea en la BD.
    Siempre retorna un JWT listo para usar.
    """
    email     = google_data.get("email")
    nombre    = google_data.get("nombre")
    google_id = google_data.get("google_id")

    if not email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datos de Google incompletos (faltan email o google_id)",
        )

    # Buscar usuario existente
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        # Registrar nuevo usuario
        usuario = Usuario(
            email=email,
            nombre=nombre or "Sin nombre",
            google_id=google_id,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    # Generar y devolver el token
    token = crear_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}


# ── Obtener usuario actual desde el token ──────────────────────────────────────
def get_usuario_actual(db: Session, token: str) -> Usuario:
    """
    Util para los endpoints protegidos: recibe el token, lo verifica
    y devuelve el objeto Usuario de la BD.
    """
    datos = verificar_token(token)
    usuario = db.query(Usuario).filter(Usuario.email == datos["email"]).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return usuario

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login/google")

class AuthService:

    @staticmethod
    def get_google_auth_url() -> str:
        return (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={GOOGLE_CLIENT_ID}"
            "&response_type=code"
            f"&redirect_uri={GOOGLE_REDIRECT_URI}"
            "&scope=openid%20email%20profile"
        )

    @staticmethod
    def handle_google_callback(code: str, db: Session) -> dict:
        token_res = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
        )
        token_json = token_res.json()
        access_token = token_json.get("access_token")

        perfil_res = httpx.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        perfil = perfil_res.json()

        return login_o_registrar_usuario(db, {
            "email": perfil.get("email"),
            "nombre": perfil.get("name"),
            "google_id": perfil.get("id"),
        })

    @staticmethod
    def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> Usuario:
        return get_usuario_actual(db, token)