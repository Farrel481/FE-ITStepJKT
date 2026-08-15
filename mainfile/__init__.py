#File utama API Hospital Operations Klinis
"""
1. Database & Skema Data Relasional (PostgreSQL)
Rancang basis data PostgreSQL dengan relasi yang tepat. Skema tabel minimal mencakup:

Specialties:

id,
name (unique, misal: Kardiologi, Penyakit Dalam),
description.


Doctors:

id,
specialty_id (FK),
full_name,
str_number (unique),
consultation_fee,
is_active.


Patients:

id,
full_name,
national_id (NIK/unique),
phone,
date_of_birth.


Appointments:

id,
doctor_id (FK),
patient_id (FK),
appointment_date (Date),
time_slot (misal: "09:00-09:30"),
status (scheduled, completed, cancelled),
notes.


Prescriptions:

id,
appointment_id (FK, One-to-One),
diagnosis,
medication_details,
total_cost.
"""
