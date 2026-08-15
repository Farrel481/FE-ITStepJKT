# Endpoint dokter dipisahkan agar main.py tetap kecil dan mudah dibaca.
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Doctor, Specialty
from app.schemas import DoctorCreate, DoctorResponse


router = APIRouter(prefix="/api/v1", tags=["Doctors"])


def doctor_to_response(doctor: Doctor, specialty_name: str) -> dict:
    """Mengubah data hasil JOIN menjadi bentuk JSON yang kita inginkan."""
    return {
        "id": doctor.id,
        "specialty_id": doctor.specialty_id,
        "specialty_name": specialty_name,
        "full_name": doctor.full_name,
        "str_number": doctor.str_number,
        "consultation_fee": float(doctor.consultation_fee),
        "is_active": doctor.is_active,
    }


@router.post(
    "/doctors",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor(doctor_data: DoctorCreate, db: Session = Depends(get_db)):
    """Mendaftarkan dokter baru ke tabel doctors."""

    # Pastikan specialty_id dari input benar-benar ada di tabel specialties.
    specialty = db.get(Specialty, doctor_data.specialty_id)
    if not specialty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spesialisasi tidak ditemukan.",
        )

    # STR dokter bersifat unik, jadi tidak boleh ada yang sama.
    existing_doctor = db.scalar(
        select(Doctor).where(Doctor.str_number == doctor_data.str_number)
    )
    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nomor STR sudah terdaftar.",
        )

    # Bentuk object Doctor menggunakan data yang sudah lolos validasi Pydantic.
    new_doctor = Doctor(
        specialty_id=doctor_data.specialty_id,
        full_name=doctor_data.full_name,
        str_number=doctor_data.str_number,
        consultation_fee=doctor_data.consultation_fee,
        is_active=doctor_data.is_active,
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    # Nama spesialisasi sudah tersedia dari query pertama di atas.
    return doctor_to_response(new_doctor, specialty.name)


@router.get("/doctors", response_model=list[DoctorResponse])
def get_doctors(
    specialty: str | None = Query(default=None, description="Filter nama spesialisasi"),
    db: Session = Depends(get_db),
):
    """Menampilkan dokter beserta nama spesialisasinya menggunakan INNER JOIN."""

    # select mengambil Doctor dan nama Specialty; join made INNER JOIN.
    query = select(Doctor, Specialty.name).join(Specialty)

    # Filter hanya dipakai jika pengguna mengirim ?specialty=Kardiologi.
    if specialty:
        query = query.where(Specialty.name.ilike(f"%{specialty}%"))

    # .all() menghasilkan daftar pasangan: (object Doctor, nama specialty).
    rows = db.execute(query).all()

    # Ubah tiap pasangan data menjadi daftar JSON yang mudah dibaca.
    result = []
    for doctor, specialty_name in rows:
        result.append(doctor_to_response(doctor, specialty_name))

    return result
