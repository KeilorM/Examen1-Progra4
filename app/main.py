from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer  # ← agregar
from app.database import engine, Base
from app.routers import pacientes, auth

Base.metadata.create_all(bind=engine)

security = HTTPBearer()

app = FastAPI(
    title="API Radiografías",
    description="API para gestión de placas radiográficas de pacientes.",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, tags=["Autenticación"])
app.include_router(pacientes.router, tags=["Pacientes"])

@app.get("/")
def root():
    return {"mensaje": "API Radiografías funcionando."}