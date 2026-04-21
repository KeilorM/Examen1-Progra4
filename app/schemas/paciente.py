from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


from fastapi import Form

class PacienteCreate(BaseModel):
    nombre_completo: str = Field(..., example="Juan Pérez Solís")
    numero_identificacion: str = Field(..., example="118240567")
    descripcion: Optional[str] = Field(None, example="Rx de tórax AP")
    fecha_estudio: date = Field(..., example="2024-04-15")

    @classmethod
    def as_form(
        cls,
        nombre_completo: str = Form(...),
        numero_identificacion: str = Form(...),
        descripcion: Optional[str] = Form(None),
        fecha_estudio: date = Form(...),
    ):
        return cls(
            nombre_completo=nombre_completo,
            numero_identificacion=numero_identificacion,
            descripcion=descripcion,
            fecha_estudio=fecha_estudio,
        )


class PacienteUpdate(BaseModel):
    nombre_completo: Optional[str] = Field(None, example="Juan Pérez Solís")
    numero_identificacion: Optional[str] = Field(None, example="118240567")
    descripcion: Optional[str] = Field(None, example="Rx de tórax AP")
    fecha_estudio: Optional[date] = Field(None, example="2024-04-15")
    imagen_url: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        nombre_completo: Optional[str] = Form(None),
        numero_identificacion: Optional[str] = Form(None),
        descripcion: Optional[str] = Form(None),
        fecha_estudio: Optional[date] = Form(None),
    ):
        return cls(
            nombre_completo=nombre_completo,
            numero_identificacion=numero_identificacion,
            descripcion=descripcion,
            fecha_estudio=fecha_estudio,
        )

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

