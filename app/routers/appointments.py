from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Doctor, Patient, Prescription
from app.schemas import (
    AppointmentCompleteResponse,
    AppointmentCreate,
    AppointmentResponse,
    PrescriptionCreate,
    PrescriptionResponse,
)


router = APIRouter(prefix="/api/v1", tags=["Appointments"])


def slots_overlap(first_slot: str, second_slot: str) -> bool:
    """Mengembalikan True jika dua rentang waktu saling bertabrakan.

    Contoh: 09:00-09:30 bentrok dengan 09:15-09:45.
    """
    first_start, first_end = first_slot.split("-")
    second_start, second_end = second_slot.split("-")

    # jam ke menit
    first_start_minutes = datetime.strptime(first_start, "%H:%M").hour * 60 + datetime.strptime(first_start, "%H:%M").minute
    first_end_minutes = datetime.strptime(first_end, "%H:%M").hour * 60 + datetime.strptime(first_end, "%H:%M").minute
    second_start_minutes = datetime.strptime(second_start, "%H:%M").hour * 60 + datetime.strptime(second_start, "%H:%M").minute
    second_end_minutes = datetime.strptime(second_end, "%H:%M").hour * 60 + datetime.strptime(second_end, "%H:%M").minute

    
    # overlap slot
    return first_start_minutes < second_end_minutes and second_start_minutes < first_end_minutes


@router.post(
    "/appointments",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
):
    """Membuat appointment setelah memeriksa dokter, pasien, dan jadwal."""
    doctor = db.get(Doctor, appointment_data.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Dokter tidak ditemukan.")
    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dokter sedang tidak aktif dan tidak dapat menerima appointment.",
        )

    patient = db.get(Patient, appointment_data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Pasien tidak ditemukan.")

    # Cari appointment scheduled dokter pada tanggal yang sama.
    # Setelah itu setiap slot dibandingkan agar overlap sebagian juga terdeteksi.
    scheduled_appointments = db.scalars(
        select(Appointment).where(
            Appointment.doctor_id == appointment_data.doctor_id,
            Appointment.appointment_date == appointment_data.appointment_date,
            Appointment.status == "scheduled",
        )
    ).all()

    for scheduled_appointment in scheduled_appointments:
        if slots_overlap(appointment_data.time_slot, scheduled_appointment.time_slot):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jadwal dokter bentrok dengan appointment scheduled yang sudah ada.",
            )

    new_appointment = Appointment(
        doctor_id=appointment_data.doctor_id,
        patient_id=appointment_data.patient_id,
        appointment_date=appointment_data.appointment_date,
        time_slot=appointment_data.time_slot,
        notes=appointment_data.notes,
        status="scheduled",
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


@router.post(
    "/appointments/{appointment_id}/complete",
    response_model=AppointmentCompleteResponse,
)
def complete_appointment(
    appointment_id: int,
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db),
):
    """Menyelesaikan appointment dan membuat resep dalam satu transaction."""
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment tidak ditemukan.")
    if appointment.status != "scheduled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hanya appointment berstatus scheduled yang dapat diselesaikan.",
        )

    existing_prescription = db.scalar(
        select(Prescription).where(Prescription.appointment_id == appointment_id)
    )
    if existing_prescription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resep untuk appointment ini sudah ada.",
        )

    # Kedua perubahan berada dalam session yang sama, permanen saat commit.
    appointment.status = "completed"
    new_prescription = Prescription(
        appointment_id=appointment.id,
        diagnosis=prescription_data.diagnosis,
        medication_details=prescription_data.medication_details,
        total_cost=prescription_data.total_cost,
    )
    db.add(new_prescription)

    try:
        db.commit()
        db.refresh(new_prescription)
    except Exception:
        # Jika update status atau pembuatan resep gagal, seluruh perubahan dibatalkan.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menyelesaikan appointment. Perubahan dibatalkan.",
        )

    return AppointmentCompleteResponse(
        appointment_id=appointment.id,
        status=appointment.status,
        prescription=PrescriptionResponse.model_validate(new_prescription),
    )
