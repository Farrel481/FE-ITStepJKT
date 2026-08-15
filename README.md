# Hospital Clinical Operations RESTful API

RESTful API untuk mengelola spesialisasi, dokter, pasien, appointment, resep,
dan laporan rekap harian rumah sakit. Dibangun menggunakan FastAPI,
PostgreSQL, SQLAlchemy, dan Pydantic.

Feel free 2 make Issue atau Pull Request!

## Relasi Database

```text
Specialty (1) ---- (*) Doctor
Doctor    (1) ---- (*) Appointment (*) ---- (1) Patient
Appointment (1) -- (1) Prescription
```

## Preparation

1. Buat database PostgreSQL bernama `hospital_api`.
2. Buat virtual environment dan instal dependency:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Salin `.env.example` menjadi `.env`, lalu isi password PostgreSQL sendiri:

```env
DATABASE_URL=postgresql+psycopg://postgres:isi-dgn-password@localhost:5432/hospital_api
```

4. Jalankan aplikasi:

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```

Buka dokumentasi `http://127.0.0.1:8000/docs`.

## Contoh Payload Endpoint Kompleks

### Buat appointment

```json
{
  "doctor_id": 1,
  "patient_id": 1,
  "appointment_date": "2026-08-13",
  "time_slot": "09:00-09:30",
  "notes": "Kontrol awal"
}
```

### Daftarkan pasien

```json
{
  "full_name": "Siti Aminah",
  "national_id": "3174011234567890",
  "phone": "081234567890",
  "date_of_birth": "1995-05-20"
}
```

### Selesaikan appointment dan buat resep

```json
{
  "diagnosis": "Hipertensi ringan",
  "medication_details": "Amlodipine 5 mg, satu kali sehari",
  "total_cost": 75000
}
```

## Endpoint

| Method | Endpoint | Kegunaan |
| --- | --- | --- |
| POST | `/api/v1/specialties` | Tambah spesialisasi |
| POST | `/api/v1/doctors` | Tambah dokter |
| GET | `/api/v1/doctors?specialty=Kardiologi` | Daftar/filter dokter dengan INNER JOIN |
| POST | `/api/v1/patients` | Daftar pasien |
| GET | `/api/v1/patients/{id}/medical-history` | Riwayat medis dengan LEFT JOIN |
| POST | `/api/v1/appointments` | Buat appointment dan cek konflik jadwal |
| POST | `/api/v1/appointments/{id}/complete` | Selesaikan appointment + buat resep atomik |
| GET | `/api/v1/reports/daily-summary?report_date=2026-08-15` | Laporan dokter harian |

## Aturan Bisnis

- Dokter harus aktif saat appointment dibuat.
- Satu dokter tidak boleh memiliki dua appointment `scheduled` pada tanggal dan
  time slot yang sama.
- Appointment hanya dapat diselesaikan sekali dan menghasilkan tepat satu resep.
- Penyelesaian appointment dan pembuatan resep disimpan dalam satu transaction.

## Keamanan Konfigurasi

File `.env` tidak diunggah ke GitHub karena sudah ada dalam `.gitignore`.
Gunakan `.env.example` sebagai contoh konfigurasi tanpa password asli.

## Riwayat Query PostgreSQL

Lihat `database_query_history.sql` untuk contoh query create database/table,
insert, select, INNER JOIN, LEFT JOIN, serta laporan agregasi.

Terimakasih.