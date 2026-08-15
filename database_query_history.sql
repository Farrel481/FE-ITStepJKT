-- Clinic & Medical Appointment API - Riwayat Query PostgreSQL
-- Jalankan CREATE DATABASE dari koneksi PostgreSQL biasa, lalu sambungkan ke hospital_api.

CREATE DATABASE hospital_api;

-- CREATE TABLE
CREATE TABLE specialties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    specialty_id INTEGER NOT NULL REFERENCES specialties(id),
    full_name VARCHAR(150) NOT NULL,
    str_number VARCHAR(50) NOT NULL UNIQUE,
    consultation_fee NUMERIC(12, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    national_id VARCHAR(50) NOT NULL UNIQUE,
    phone VARCHAR(30) NOT NULL,
    date_of_birth DATE NOT NULL
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id),
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    appointment_date DATE NOT NULL,
    time_slot VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    notes TEXT,
    CONSTRAINT valid_appointment_status
        CHECK (status IN ('scheduled', 'completed', 'cancelled'))
);

CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    appointment_id INTEGER NOT NULL UNIQUE REFERENCES appointments(id),
    diagnosis TEXT NOT NULL,
    medication_details TEXT NOT NULL,
    total_cost NUMERIC(12, 2) NOT NULL
);

-- INSERT TABLE
INSERT INTO specialties (name, description)
VALUES ('Kardiologi', 'Penanganan jantung dan pembuluh darah');

INSERT INTO doctors (specialty_id, full_name, str_number, consultation_fee, is_active)
VALUES (1, 'dr. Budi Santoso', 'STR-1234567890', 150000, TRUE);

INSERT INTO patients (full_name, national_id, phone, date_of_birth)
VALUES ('Siti Aminah', '3174011234567890', '081234567890', '1995-05-20');

-- SELECT TABLE
SELECT * FROM specialties;
SELECT * FROM doctors;
SELECT * FROM patients;
SELECT * FROM appointments;
SELECT * FROM prescriptions;

-- INNER JOIN: dokter dan spesialisasinya
SELECT doctors.id, doctors.full_name, doctors.str_number,
       doctors.consultation_fee, doctors.is_active,
       specialties.name AS specialty_name
FROM doctors
INNER JOIN specialties ON doctors.specialty_id = specialties.id;

-- LEFT JOIN bertingkat: riwayat medis pasien
SELECT patients.full_name AS patient_name,
       appointments.appointment_date, appointments.time_slot, appointments.status,
       doctors.full_name AS doctor_name,
       prescriptions.diagnosis, prescriptions.medication_details,
       prescriptions.total_cost
FROM patients
LEFT JOIN appointments ON patients.id = appointments.patient_id
LEFT JOIN prescriptions ON appointments.id = prescriptions.appointment_id
LEFT JOIN doctors ON appointments.doctor_id = doctors.id
WHERE patients.id = 1;

-- dailysummary
SELECT doctors.id, doctors.full_name, specialties.name AS specialty_name,
       COUNT(appointments.id) AS total_patients,
       SUM(doctors.consultation_fee + COALESCE(prescriptions.total_cost, 0))
           AS total_revenue
FROM doctors
INNER JOIN specialties ON doctors.specialty_id = specialties.id
INNER JOIN appointments ON appointments.doctor_id = doctors.id
LEFT JOIN prescriptions ON prescriptions.appointment_id = appointments.id
WHERE appointments.appointment_date = '2026-08-15'
  AND appointments.status = 'completed'
GROUP BY doctors.id, doctors.full_name, specialties.name;
