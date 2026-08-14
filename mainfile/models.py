from datetime import date
from decimal import Decimal
from sqlalchemy import Boolean, Date, Numeric, CheckConstraint, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.database import Base

class Specialty(Base):
  __tablename__ = "specialties"

class Doctor(Base):
  __tablename__ = "doctors"

class Patient(Base):
  __tablename__ = "patients"

class Appointment(Base):
  __tablename__ = "appointments"

class Prescription(Base):
  __tablename__ = "prescriptions"
