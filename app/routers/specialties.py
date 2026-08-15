# APIRouter dipakai agar endpoint Specialty terpisah dari file main.py.
from fastapi import APIRouter, Depends, HTTPException, status

# select membuat query SELECT dengan gaya SQLAlchemy ORM.
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Specialty
from app.schemas import SpecialtyCreate, SpecialtyResponse


# Semua endpoint di file ini otomatis dimulai dengan /api/v1.
router = APIRouter(prefix="/api/v1", tags=["Specialties"])


@router.post(
    "/specialties",
    response_model=SpecialtyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_specialty(
    specialty_data: SpecialtyCreate,
    db: Session = Depends(get_db),
):
    """Menyimpan satu spesialisasi baru ke tabel specialties."""

    # Cek dulu supaya nama spesialisasi yang sama tidak tersimpan dua kali.
    existing_specialty = db.scalar(
        select(Specialty).where(Specialty.name == specialty_data.name)
    )

    # Jika hasil query ada, hentikan proses dan kirim error 400.
    if existing_specialty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama spesialisasi sudah terdaftar.",
        )

    # Buat object Python dari data yang dikirim pengguna.
    new_specialty = Specialty(
        name=specialty_data.name,
        description=specialty_data.description,
    )

    # Object ke antrean database.
    db.add(new_specialty)
    db.commit()
    db.refresh(new_specialty)
    return new_specialty
