from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    google_id = Column(String, unique=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

    pacientes = relationship("Paciente", back_populates="usuario")


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False)
    numero_identificacion = Column(String, unique=True, nullable=False)
    descripcion = Column(String, nullable=True)
    fecha_estudio = Column(Date, nullable=False)
    imagen_url = Column(String, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="pacientes")