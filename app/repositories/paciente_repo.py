from sqlalchemy.orm import Session
from app.models import Paciente

def get_all(db: Session):
    return db.query(Paciente).all()

def get_by_id(db: Session, paciente_id: int):
    return db.query(Paciente).filter(Paciente.id == paciente_id).first()

def create(db: Session, data: dict):
    paciente = Paciente(**data)
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return paciente

def update(db: Session, paciente_id: int, data: dict):
    paciente = get_by_id(db, paciente_id)
    if paciente:
        for key, value in data.items():
            setattr(paciente, key, value)
        db.commit()
        db.refresh(paciente)
    return paciente

def delete(db: Session, paciente_id: int):
    paciente = get_by_id(db, paciente_id)
    if paciente:
        db.delete(paciente)
        db.commit()
    return paciente