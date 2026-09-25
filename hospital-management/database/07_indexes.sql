-- =============================================================================
-- 07_indexes.sql
-- Speeds up the three hottest look-ups in this system:
--   • searching patients by name
--   • joining / filtering by doctor_id
--   • listing a day's appointments
-- =============================================================================

USE hospital_db;

-- Patient search (name OR phone). Phone already has a UNIQUE index from DDL.
CREATE INDEX idx_patient_first_name ON patients (first_name);
CREATE INDEX idx_patient_last_name  ON patients (last_name);

-- Composite covering the common "search by full name" pattern
CREATE INDEX idx_patient_name ON patients (first_name, last_name);

-- doctor_id is already indexed as a PK on doctors; this one speeds
-- appointment lists grouped by doctor.
CREATE INDEX idx_appointments_doctor_id ON appointments (doctor_id);

-- Dashboard "today's appointments" and doctor_schedule view
CREATE INDEX idx_appointment_date ON appointments (appointment_date);

-- Composite used by the double-booking check (doctor + date + time)
CREATE INDEX idx_appointments_slot ON appointments (doctor_id, appointment_date, appointment_time, status);

-- Billing desk filters
CREATE INDEX idx_bills_status ON bills (status);
CREATE INDEX idx_bills_patient ON bills (patient_id);
