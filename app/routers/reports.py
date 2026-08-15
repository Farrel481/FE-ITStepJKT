from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Doctor, Prescription, Specialty
from app.schemas import DailySummaryResponse


router = APIRouter(prefix="/api/v1", tags=["Reports"])


@router.get("/reports/daily-summary", response_model=list[DailySummaryResponse])
def get_daily_summary(report_date: date, db: Session = Depends(get_db)):
    """Membuat laporan dokter yang menangani appointment completed pada satu tanggal."""
    # COALESCE mengganti total resep yang kosong menjadi 0 agar penjumlahan aman.
    prescription_cost = func.coalesce(Prescription.total_cost, 0)
    total_revenue = func.sum(Doctor.consultation_fee + prescription_cost).label(
        "total_revenue"
    )

    # Query ini memakai JOIN, LEFT JOIN, GROUP BY, COUNT, dan SUM.
    query = (
        select(
            Doctor.id,
            Doctor.full_name,
            Specialty.name,
            func.count(Appointment.id).label("total_patients"),
            total_revenue,
        )
        .join(Specialty, Doctor.specialty_id == Specialty.id)
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .outerjoin(Prescription, Prescription.appointment_id == Appointment.id)
        .where(
            Appointment.appointment_date == report_date,
            Appointment.status == "completed",
        )
        .group_by(Doctor.id, Doctor.full_name, Specialty.name)
        .order_by(Doctor.full_name)
    )
    rows = db.execute(query).all()

    result = []
    for doctor_id, doctor_name, specialty_name, total_patients, revenue in rows:
        result.append(
            DailySummaryResponse(
                doctor_id=doctor_id,
                doctor_name=doctor_name,
                specialty_name=specialty_name,
                report_date=report_date,
                total_patients=total_patients,
                total_revenue=float(revenue),
            )
        )
    return result
