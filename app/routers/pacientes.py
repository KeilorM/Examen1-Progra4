from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.paciente import PacienteCreate, PacienteResponse, PacienteUpdate
from app.services.auth_service import AuthService
from app.services.paciente_service import PacienteService

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"],
    dependencies=[Depends(AuthService.get_current_user)],
)


@router.post(
    "/",
    response_model=PacienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo paciente",
    description=(
        "Crea un nuevo registro de paciente con su placa radiográfica. "
        "La imagen debe enviarse como multipart/form-data. "
        "Se valida el tipo (image/jpeg, image/png) y el tamaño máximo (5 MB). "
        "La imagen se sube a Cloudinary y la URL pública se persiste en la BD."
    ),
)
def crear_paciente(
    datos: PacienteCreate = Depends(PacienteCreate.as_form),
    imagen: UploadFile = File(..., description="Placa radiográfica (JPEG o PNG, máx. 5 MB)"),
    db: Session = Depends(get_db),
):
    return PacienteService.crear(datos=datos, imagen=imagen, db=db)


@router.get(
    "/",
    response_model=list[PacienteResponse],
    summary="Listar pacientes",
    description=(
        "Devuelve una lista paginada de pacientes. "
        "Soporta filtro por nombre y ordenamiento por fecha de estudio."
    ),
)
def listar_pacientes(
    nombre: Optional[str] = Query(None, description="Filtrar por nombre (búsqueda parcial)"),
    orden: Optional[str] = Query(
        "desc",
        description="Ordenar por fecha_estudio: 'asc' o 'desc'",
        pattern="^(asc|desc)$",
    ),
    pagina: int = Query(1, ge=1, description="Número de página (empieza en 1)"),
    por_pagina: int = Query(10, ge=1, le=100, description="Registros por página (máx. 100)"),
    db: Session = Depends(get_db),
):
    return PacienteService.listar(
        db=db, nombre=nombre, orden=orden, pagina=pagina, por_pagina=por_pagina
    )


@router.get(
    "/{paciente_id}",
    response_model=PacienteResponse,
    summary="Obtener un paciente por ID",
    description="Devuelve el detalle completo de un paciente, incluyendo la URL de su placa radiográfica.",
)
def obtener_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = PacienteService.obtener_por_id(paciente_id=paciente_id, db=db)
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con id {paciente_id} no encontrado.",
        )
    return paciente


@router.put(
    "/{paciente_id}",
    response_model=PacienteResponse,
    summary="Actualizar un paciente",
    description=(
        "Actualiza los datos de un paciente existente. "
        "Si se envía una nueva imagen, la anterior en Cloudinary se reemplaza."
    ),
)
def actualizar_paciente(
    paciente_id: int,
    datos: PacienteUpdate = Depends(PacienteUpdate.as_form),
    imagen: Optional[UploadFile] = File(None, description="Nueva placa (opcional)"),
    db: Session = Depends(get_db),
):
    paciente = PacienteService.actualizar(
        paciente_id=paciente_id, datos=datos, imagen=imagen, db=db
    )
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con id {paciente_id} no encontrado.",
        )
    return paciente


@router.delete(
    "/{paciente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un paciente",
    description="Elimina el registro del paciente y la imagen asociada en Cloudinary.",
)
def eliminar_paciente(paciente_id: int, db: Session = Depends(get_db)):
    eliminado = PacienteService.eliminar(paciente_id=paciente_id, db=db)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con id {paciente_id} no encontrado.",
        )