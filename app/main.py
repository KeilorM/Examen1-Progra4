from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.database import engine, Base
from app.routers import pacientes, auth
from fastapi.responses import RedirectResponse
from app.scheduler import iniciar_scheduler

Base.metadata.create_all(bind=engine)

security = HTTPBearer()

app = FastAPI(
    title="API Radiografías",
    description="API para gestión de placas radiográficas de pacientes.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Autenticación"])
app.include_router(pacientes.router, tags=["Pacientes"])

@app.on_event("startup")
def startup_event():
    iniciar_scheduler()

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.on_event("startup")
def startup_event():
    import subprocess
    subprocess.run(["alembic", "upgrade", "head"])
    iniciar_scheduler()