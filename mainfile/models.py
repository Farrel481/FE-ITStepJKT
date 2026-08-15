from datetime import date
from decimal import Decimal
from sqlalchemy import Boolean, Date, Numeric, CheckConstraint, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, relationship, mapped_column
from mainfile.database import Base

class Specialty(Base):
    __tablename__ = "specialties"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    doctors: Mapped[list["Doctor"]] = relationship(back_populates="specialty")

class Doctor(Base):
    __tablename__ = "doctors"
    id: Mapped[int] = mapped_column(primary_key=True)
    specialty_id: Mapped[int] = mapped_column(ForeignKey("specialties.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), index=True)
    str_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    consultation_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    specialty: Mapped["Specialty"] = relationship(back_populates="doctors")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")

class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), index=True)
    national_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(30))
    d_o_b: Mapped[date] = mapped_column(Date, nullable=False)
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")
  
class Appointment(Base):
  __tablename__ = "appointments"

class Prescription(Base):
  __tablename__ = "prescriptions"
