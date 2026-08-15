from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401 - mendaftarkan seluruh model pada Base.metadata
from app.database import Base, engine
from app.routers.appointments import router as appointments_router
from app.routers.doctors import router as doctors_router
from app.routers.patients import router as patients_router
from app.routers.reports import router as reports_router
from app.routers.specialties import router as specialties_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Membuat tabel bila belum ada saat API pertama kali berjalan."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Hospital Clinical Operations API",
    version="1.0.0",
    description="API untuk mengelola operasional klinis rumah sakit.",
    lifespan=lifespan,
)

# Menghubungkan endpoint Specialty ke aplikasi utama.
app.include_router(specialties_router)
# Menghubungkan endpoint Doctor ke aplikasi utama.
app.include_router(doctors_router)
# Menghubungkan endpoint Patient, Appointment, dan Report ke aplikasi utama.
app.include_router(patients_router)
app.include_router(appointments_router)
app.include_router(reports_router)


@app.get("/", tags=["Health Check"])
def health_check():
    return {"message": "Hospital Clinical Operations API is running"}
