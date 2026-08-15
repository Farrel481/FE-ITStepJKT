from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Doctor, Patient, Prescription
from app.schemas import (
    MedicalHistoryItem,
    MedicalHistoryResponse,
    PatientCreate,
    PatientResponse,
)


router = APIRouter(prefix="/api/v1", tags=["Patients"])


@router.post(
    "/patients",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    """Mendaftarkan pasien baru dan memastikan NIK tidak ganda."""
    existing_patient = db.scalar(
        select(Patient).where(Patient.national_id == patient_data.national_id)
    )
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nomor identitas pasien sudah terdaftar.",
        )

    new_patient = Patient(
        full_name=patient_data.full_name,
        national_id=patient_data.national_id,
        phone=patient_data.phone,
        date_of_birth=patient_data.date_of_birth,
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient


@router.get("/patients/{patient_id}/medical-history", response_model=MedicalHistoryResponse)
def get_medical_history(patient_id: int, db: Session = Depends(get_db)):
    """Mengambil riwayat dengan LEFT JOIN agar appointment tanpa resep tetap tampil."""
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pasien tidak ditemukan.",
        )

    # LEFT JOIN connection: patients -> appointments -> prescriptions -> doctors.
    query = (
        select(Patient, Appointment, Prescription, Doctor)
        .outerjoin(Appointment, Patient.id == Appointment.patient_id)
        .outerjoin(Prescription, Appointment.id == Prescription.appointment_id)
        .outerjoin(Doctor, Appointment.doctor_id == Doctor.id)
        .where(Patient.id == patient_id)
        .order_by(Appointment.appointment_date.desc(), Appointment.time_slot.desc())
    )
    rows = db.execute(query).all()

    history = []
    for _, appointment, prescription, doctor in rows:
        # Jika pasien belum pernah appointment, LEFT JOIN appointment = None.
        if appointment is None:
            continue
        history.append(
            MedicalHistoryItem(
                appointment_id=appointment.id,
                appointment_date=appointment.appointment_date,
                time_slot=appointment.time_slot,
                status=appointment.status,
                notes=appointment.notes,
                doctor_id=doctor.id if doctor else None,
                doctor_name=doctor.full_name if doctor else None,
                diagnosis=prescription.diagnosis if prescription else None,
                medication_details=prescription.medication_details if prescription else None,
                total_cost=float(prescription.total_cost) if prescription else None,
            )
        )

    return MedicalHistoryResponse(
        patient=PatientResponse.model_validate(patient),
        appointments=history,
    )
