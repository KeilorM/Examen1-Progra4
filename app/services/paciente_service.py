import cloudinary
import cloudinary.uploader
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
#ze zuve la imagen
def subir_imagen(archivo: UploadFile) -> str:
    """
    Valida y sube una imagen a Cloudinary.
    Devuelve la URL pública (CDN).
    """
    # Validar tipo
    if archivo.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido: {archivo.content_type}. "
                   f"Use: {', '.join(TIPOS_PERMITIDOS)}",
        )

    # Leer contenido y validar tamaño
    contenido = archivo.file.read()
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo supera el tamaño máximo de {TAMANO_MAXIMO_MB} MB",
        )

    # Subir a Cloudinary
    try:
        resultado = cloudinary.uploader.upload(
            contenido,
            folder="radiografias",       # carpeta en tu cuenta Cloudinary
            resource_type="image",
        )
        return resultado["secure_url"]   # URL HTTPS del CDN
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al subir imagen a Cloudinary: {str(e)}",
        )


# ── CRUD ───────────────────────────────────────────────────────────────────────

def obtener_todos(db: Session, skip: int = 0, limit: int = 10, nombre: str = None):
    """Lista paginada de pacientes, con filtro opcional por nombre."""
    return paciente_repo.get_all(db, skip=skip, limit=limit, nombre=nombre)


def obtener_por_id(db: Session, paciente_id: int):
    """Devuelve un paciente por ID o lanza 404."""
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
    """
    Crea un nuevo paciente.
    Si se adjunta imagen, la sube a Cloudinary y guarda la URL.
    """
    imagen_url = None
    if imagen and imagen.filename:
        imagen_url = subir_imagen(imagen)

    data_dict = datos.model_dump()
    data_dict["usuario_id"] = usuario_id
    data_dict["imagen_url"] = imagen_url

    return paciente_repo.create(db, data_dict)


def actualizar_paciente(
    db: Session,
    paciente_id: int,
    datos: PacienteUpdate,
    imagen: UploadFile = None,
):
    """
    Actualiza campos de un paciente.
    Si se adjunta nueva imagen, reemplaza la URL en Cloudinary.
    """
    # Verificar que existe
    obtener_por_id(db, paciente_id)

    data_dict = datos.model_dump(exclude_unset=True)  # solo campos enviados

    if imagen and imagen.filename:
        data_dict["imagen_url"] = subir_imagen(imagen)

    actualizado = paciente_repo.update(db, paciente_id, data_dict)
    if not actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se pudo actualizar el paciente",
        )
    return actualizado


def eliminar_paciente(db: Session, paciente_id: int):
    """Elimina un paciente. Lanza 404 si no existe."""
    eliminado = paciente_repo.delete(db, paciente_id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {paciente_id} no encontrado",
        )
    return {"mensaje": f"Paciente {paciente_id} eliminado correctamente"}