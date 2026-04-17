# Examen1-Progra4
# API Radiografías

## Descripción
API para gestión de placas radiográficas de pacientes.

## Instalación
1. git clone ...
2. python -m venv venv
3. venv\Scripts\activate
4. pip install -r requirements.txt
5. Crear .env con las claves
6. alembic upgrade head
7. uvicorn app.main:app --reload

## Tecnologías
- FastAPI
- SQLite + SQLAlchemy + Alembic
- Cloudinary
- Google OAuth2 + JWT

## Decisiones técnicas
- FastAPI en lugar de Django por compatibilidad con SQLAlchemy y Pydantic
- SQLite para simplicidad en desarrollo
- Cloudinary para CDN de imágenes