from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.get(
    "/login/google",
    summary="Iniciar sesión con Google",
    description="Redirige al usuario al flujo de autenticación de Google (SSO).",
)
def login_with_google():
    auth_url = AuthService.get_google_auth_url()
    return RedirectResponse(url=auth_url)


@router.get(
    "/callback",
    summary="Callback de Google OAuth2",
    description=(
        "Google redirige aquí tras la autenticación. "
        "Se intercambia el código por un token de Google, "
        "se obtiene el perfil del usuario y se genera un JWT propio."
    ),
    response_description="JWT de acceso para usar en endpoints protegidos.",
)
def google_callback(code: str, db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de autorización no recibido.",
        )
    token_data = AuthService.handle_google_callback(code=code, db=db)
    return token_data


@router.get(
    "/me",
    summary="Información del usuario autenticado",
    description="Devuelve los datos del usuario a partir del JWT enviado en el header.",
)
def get_current_user(current_user=Depends(AuthService.get_current_user)):
    return current_user