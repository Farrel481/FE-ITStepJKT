# BaseModel adalah "cetakan" data dari dan ke API.
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Schema ini dipakai saat pengguna membuat spesialisasi baru.
class SpecialtyCreate(BaseModel):
    # Nama wajib diisi, minimal 3 dan maksimal 100 karakter.
    name: str = Field(min_length=3, max_length=100)

    # Deskripsi boleh tidak diisi, maka nilai awalnya None/kosong.
    description: str | None = Field(default=None, max_length=500)


# Schema ini dipakai saat API mengirim data spesialisasi sebagai response.
class SpecialtyResponse(BaseModel):
    # id dibuat otomatis oleh PostgreSQL setelah data disimpan.
    id: int
    name: str
    description: str | None

    # Mengizinkan Pydantic membaca data langsung dari object SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)


# Schema ini dipakai saat pengguna menambahkan dokter baru.
class DoctorCreate(BaseModel):
    # Nomor id spesialisasi yang dipilih untuk dokter ini.
    specialty_id: int = Field(gt=0)
    full_name: str = Field(min_length=3, max_length=150)
    # STR harus unik. Pemeriksaan data yang sama dilakukan di router.
    str_number: str = Field(min_length=5, max_length=50)
    # Biaya konsultasi tidak boleh nol atau negatif.
    consultation_fee: float = Field(gt=0)
    # Jika tidak dikirim, dokter dianggap aktif.
    is_active: bool = True


# Bentuk data dokter yang dikirim API ke pengguna.
class DoctorResponse(BaseModel):
    id: int
    specialty_id: int
    # Ini berasal dari tabel specialties melalui INNER JOIN.
    specialty_name: str
    full_name: str
    str_number: str
    consultation_fee: float
    is_active: bool


# Schema untuk mendaftarkan pasien baru.
class PatientCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=150)
    national_id: str = Field(min_length=5, max_length=50)
    phone: str = Field(min_length=8, max_length=30)
    # Pydantic akan memastikan formatnya YYYY-MM-DD.
    date_of_birth: date

    @field_validator("date_of_birth")
    @classmethod
    def date_of_birth_cannot_be_future(cls, value: date) -> date:
        """Tanggal lahir tidak boleh melebihi tanggal hari ini."""
        if value > date.today():
            raise ValueError("Tanggal lahir tidak boleh di masa depan.")
        return value


class PatientResponse(BaseModel):
    id: int
    full_name: str
    national_id: str
    phone: str
    date_of_birth: date

    model_config = ConfigDict(from_attributes=True)


# Schema untuk membuat janji temu.
class AppointmentCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    patient_id: int = Field(gt=0)
    appointment_date: date
    # Contoh time_slot: 09:00-09:30
    time_slot: str = Field(min_length=11, max_length=11)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("time_slot")
    @classmethod
    def validate_time_slot(cls, value: str) -> str:
        """Memastikan format slot waktu benar dan jam akhir lebih besar."""
        try:
            start_text, end_text = value.split("-")
            start_time = datetime.strptime(start_text, "%H:%M").time()
            end_time = datetime.strptime(end_text, "%H:%M").time()
        except ValueError as error:
            raise ValueError("time_slot harus berformat HH:MM-HH:MM.") from error

        if end_time <= start_time:
            raise ValueError("Jam akhir harus lebih besar dari jam mulai.")
        return value


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_date: date
    time_slot: str
    status: str
    notes: str | None

    model_config = ConfigDict(from_attributes=True)


# Data resep dikirim ketika appointment diselesaikan.
class PrescriptionCreate(BaseModel):
    diagnosis: str = Field(min_length=3, max_length=1000)
    medication_details: str = Field(min_length=3, max_length=2000)
    total_cost: float = Field(ge=0)


class PrescriptionResponse(BaseModel):
    id: int
    appointment_id: int
    diagnosis: str
    medication_details: str
    total_cost: float

    model_config = ConfigDict(from_attributes=True)


class AppointmentCompleteResponse(BaseModel):
    appointment_id: int
    status: str
    prescription: PrescriptionResponse


# Satu item appointment untuk endpoint riwayat medis pasien.
class MedicalHistoryItem(BaseModel):
    appointment_id: int
    appointment_date: date
    time_slot: str
    status: str
    notes: str | None
    doctor_id: int | None
    doctor_name: str | None
    diagnosis: str | None
    medication_details: str | None
    total_cost: float | None


class MedicalHistoryResponse(BaseModel):
    patient: PatientResponse
    appointments: list[MedicalHistoryItem]


# Satu baris untuk laporan pendapatan dokter per hari.
class DailySummaryResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    specialty_name: str
    report_date: date
    total_patients: int
    total_revenue: float
