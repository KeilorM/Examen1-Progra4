from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import RedirectResponse

try:
    from app.database import engine, Base
    from app.routers import pacientes, auth
    from app.scheduler import iniciar_scheduler
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"ERROR EN IMPORTS: {e}")
    raise

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = iniciar_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="API Radiografías",
    description="API para gestión de placas radiográficas de pacientes.",
    version="1.0.0",
    lifespan=lifespan,
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
app.include_router(pacientes.router_publico, tags=["Pacientes"])