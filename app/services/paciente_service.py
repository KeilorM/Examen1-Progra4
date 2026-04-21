import time
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.repositories import paciente_repo
from app.schemas.paciente import PacienteCreate, PacienteUpdate
import os

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key    = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
)

TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp", "image/gif"}
TAMANO_MAXIMO_MB = 5
TAMANO_MAXIMO_BYTES = TAMANO_MAXIMO_MB * 1024 * 1024

# ── Subida de imagen ──────────────────────────────────────────────────────────
def subir_imagen(archivo: UploadFile) -> dict:
    """
    Valida y sube una imagen a Cloudinary.
    Devuelve un dict con URL y public_id.
    """
    if archivo.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido: {archivo.content_type}. "
                   f"Use: {', '.join(TIPOS_PERMITIDOS)}",
        )

    contenido = archivo.file.read()
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo supera el tamaño máximo de {TAMANO_MAXIMO_MB} MB",
        )

    try:
        resultado = cloudinary.uploader.upload(
        contenido,
        folder="radiografias",
        resource_type="image",
        type="authenticated",
    )
        return {
            "url": resultado["secure_url"],
            "public_id": resultado["public_id"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al subir imagen a Cloudinary: {str(e)}",
        )


# ── URL firmada ───────────────────────────────────────────────────────────────
def generar_url_firmada(public_id: str, expiracion_minutos: int = 10) -> str:
    """
    Genera una URL firmada con expiración para acceder a imagen privada.
    """
    expiracion = int(time.time()) + (expiracion_minutos * 60)

    url = cloudinary.utils.cloudinary_url(
        public_id,
        type="authenticated",
        sign_url=True,
        expires_at=expiracion,
    )[0]
    return url


# ── CRUD ───────────────────────────────────────────────────────────────────────

def obtener_todos(db: Session, skip: int = 0, limit: int = 10, nombre: str = None):
    return paciente_repo.get_all(db, skip=skip, limit=limit, nombre=nombre)


def obtener_por_id(db: Session, paciente_id: int):
    paciente = paciente_repo.get_by_id(db, paciente_id)
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {paciente_id} no encontrado",
        )
    return paciente


def crear_paciente(
    db: Session,
    datos: PacienteCreate,
    usuario_id: int,
    imagen: UploadFile = None,
):
    imagen_url = None
    public_id = None

    if imagen and imagen.filename:
        imagen_data = subir_imagen(imagen)
        imagen_url = imagen_data["url"]
        public_id = imagen_data["public_id"]

    data_dict = datos.model_dump()
    data_dict["usuario_id"] = usuario_id
    data_dict["imagen_url"] = imagen_url
    data_dict["public_id"] = public_id

    return paciente_repo.create(db, data_dict)


def actualizar_paciente(
    db: Session,
    paciente_id: int,
    datos: PacienteUpdate,
    imagen: UploadFile = None,
):
    obtener_por_id(db, paciente_id)

    data_dict = datos.model_dump(exclude_unset=True)

    if imagen and imagen.filename:
        imagen_data = subir_imagen(imagen)
        data_dict["imagen_url"] = imagen_data["url"]
        data_dict["public_id"] = imagen_data["public_id"]

    actualizado = paciente_repo.update(db, paciente_id, data_dict)
    if not actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se pudo actualizar el paciente",
        )
    return actualizado


def eliminar_paciente(db: Session, paciente_id: int):
    eliminado = paciente_repo.delete(db, paciente_id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {paciente_id} no encontrado",
        )
    return {"mensaje": f"Paciente {paciente_id} eliminado correctamente"}


class PacienteService:

    @staticmethod
    def crear(datos, imagen, db):
        return crear_paciente(db=db, datos=datos, usuario_id=1, imagen=imagen)

    @staticmethod
    def listar(db, nombre, orden, pagina, por_pagina):
        skip = (pagina - 1) * por_pagina
        return obtener_todos(db=db, skip=skip, limit=por_pagina, nombre=nombre)

    @staticmethod
    def obtener_por_id(paciente_id, db):
        return obtener_por_id(db=db, paciente_id=paciente_id)

    @staticmethod
    def actualizar(paciente_id, datos, imagen, db):
        return actualizar_paciente(db=db, paciente_id=paciente_id, datos=datos, imagen=imagen)

    @staticmethod
    def eliminar(paciente_id, db):
        return eliminar_paciente(db=db, paciente_id=paciente_id)

    @staticmethod
    def obtener_url_firmada(paciente_id: int, expiracion_minutos: int, db: Session):
        paciente = obtener_por_id(db=db, paciente_id=paciente_id)
        if not paciente.public_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Este paciente no tiene imagen asociada",
            )
        url = generar_url_firmada(paciente.public_id, expiracion_minutos)
        return {"url_firmada": url, "expira_en_minutos": expiracion_minutos}


# ── Job para hacer imágenes privadas ──────────────────────────────────────────
def hacer_imagenes_privadas(db: Session):
    """
    Cambia todas las imágenes a privadas en Cloudinary.
    Se ejecuta automáticamente a las 11:59.
    """
    from app.models import Paciente
    pacientes = db.query(Paciente).filter(
        Paciente.public_id != None
    ).all()

    for paciente in pacientes:
        try:
            cloudinary.uploader.explicit(
                paciente.public_id,
                type="authenticated",
                access_control=[{"access_type": "token"}]
            )
            print(f"Imagen ocultada: {paciente.public_id} ✅")
        except Exception as e:
            print(f"Error ocultando imagen {paciente.public_id}: {e}")