from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import check_db_connection
from app.modules.admin.router import router as admin_router
from app.modules.appointments.router import router as appointments_router
from app.modules.availability.router import router as availability_router
from app.modules.doctors.router import router as doctors_router
from app.modules.specialties.router import router as specialties_router
from app.modules.users.router import auth_router, router as users_router

app = FastAPI(
    title="Agenda Fácil API",
    description="API REST para gerenciamento de consultas médicas — BUGBUSTERS",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(specialties_router)
app.include_router(doctors_router)
app.include_router(availability_router)
app.include_router(appointments_router)
app.include_router(admin_router)


@app.get("/health", tags=["infra"])
def health():
    db_ok = check_db_connection()
    return {
        "status": "ok",
        "db": "ok" if db_ok else "error",
        "version": "0.1.0",
    }
