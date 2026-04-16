from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class PacienteCreate(BaseModel):
    nombre_completo: str = Field(..., example="Juan Pérez Solís")
    numero_identificacion: str = Field(..., example="118240567")
    descripcion: Optional[str] = Field(None, example="Rx de tórax AP, paciente con dolor torácico")
    fecha_estudio: date = Field(..., example="2024-04-15")


class PacienteUpdate(BaseModel):
    nombre_completo: Optional[str] = Field(None, example="Juan Pérez Solís")
    numero_identificacion: Optional[str] = Field(None, example="118240567")
    descripcion: Optional[str] = Field(None, example="Rx de tórax AP")
    fecha_estudio: Optional[date] = Field(None, example="2024-04-15")
    imagen_url: Optional[str] = Field(None, example="https://res.cloudinary.com/demo/image/upload/sample.jpg")


class PacienteResponse(BaseModel):
    id: int
    nombre_completo: str
    numero_identificacion: str
    descripcion: Optional[str] = None
    fecha_estudio: date
    imagen_url: Optional[str] = None
    creado_en: datetime
    actualizado_en: datetime
    usuario_id: int

    class Config:
        from_attributes = True


class UsuarioBase(BaseModel):
    email: str
    nombre: str


class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str
    creado_en: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None