# Examen1-Progra4
# API Radiografías

## Descripción
API para gestión de placas radiográficas de pacientes.

## Instalación
1. git clone https://github.com/KeilorM/Examen1-Progra4.git
2. python -m venv venv
3. venv\Scripts\activate
4. pip install -r requirements.txt
5. Crear .env con las claves (Las credenciales debe solicitarlas a alguno de los estudiantes del grupo).
6. alembic upgrade head
7. uvicorn app.main:app --reload (Te despliega un link en localhost para poder ver la API).

## Variables de entorno
Crear archivo `.env` con:
SECRET_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

## URL de producción
https://examen1-progra4.onrender.com

## Tecnologías
- FastAPI
- SQLite + SQLAlchemy + Alembic
- Cloudinary
- Google OAuth2 + JWT

## Lenguage
Python 3.13.7

## Decisiones técnicas
- FastAPI en lugar de Django por compatibilidad con SQLAlchemy y Pydantic.
- SQLite para simplicidad en desarrollo.
- Cloudinary para CDN de imágenes.
- Google Cloud para autenticación SSO.