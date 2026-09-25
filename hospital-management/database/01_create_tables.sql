-- =============================================================================
-- Hospital Patient & Appointment Management System
-- 01_create_tables.sql  —  DDL (3NF) with PK, FK, UNIQUE, CHECK, DEFAULT
-- Engine: MySQL 8.0+
-- =============================================================================

CREATE DATABASE IF NOT EXISTS hospital_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE hospital_db;

-- Drop in child → parent order so FK checks never fail on re-run
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS payment_audit;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS treatments;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- 1. users  — authentication (Admin / Doctor / Receptionist)
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    user_id         INT             NOT NULL AUTO_INCREMENT,
    username        VARCHAR(50)     NOT NULL,
    email           VARCHAR(100)    NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    role            ENUM('ADMIN', 'DOCTOR', 'RECEPTIONIST') NOT NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_users PRIMARY KEY (user_id),
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT chk_users_username CHECK (CHAR_LENGTH(username) >= 3)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2. departments  — lookup table (avoids storing dept name on doctors → 3NF)
-- -----------------------------------------------------------------------------
CREATE TABLE departments (
    department_id   INT             NOT NULL AUTO_INCREMENT,
    name            VARCHAR(80)     NOT NULL,
    description     VARCHAR(255)    NULL,
    floor           VARCHAR(20)     NOT NULL DEFAULT '1',
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_departments PRIMARY KEY (department_id),
    CONSTRAINT uq_departments_name UNIQUE (name)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 3. doctors  — 1:1 with users, N:1 with departments
-- -----------------------------------------------------------------------------
CREATE TABLE doctors (
    doctor_id           INT             NOT NULL AUTO_INCREMENT,
    user_id             INT             NOT NULL,
    department_id       INT             NOT NULL,
    first_name          VARCHAR(60)     NOT NULL,
    last_name           VARCHAR(60)     NOT NULL,
    specialization      VARCHAR(80)     NOT NULL,
    qualification       VARCHAR(80)     NOT NULL,
    phone               VARCHAR(15)     NOT NULL,
    available_from      TIME            NOT NULL DEFAULT '09:00:00',
    available_to        TIME            NOT NULL DEFAULT '17:00:00',
    consultation_fee    DECIMAL(10,2)   NOT NULL DEFAULT 500.00,
    is_available        BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_doctors PRIMARY KEY (doctor_id),
    CONSTRAINT uq_doctors_user UNIQUE (user_id),
    CONSTRAINT uq_doctors_phone UNIQUE (phone),
    CONSTRAINT fk_doctors_user
        FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_doctors_department
        FOREIGN KEY (department_id) REFERENCES departments (department_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_doctors_fee CHECK (consultation_fee >= 0),
    CONSTRAINT chk_doctors_hours CHECK (available_to > available_from)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 4. patients  — no derived attributes (age is computed from dob → 3NF)
-- -----------------------------------------------------------------------------
CREATE TABLE patients (
    patient_id          INT             NOT NULL AUTO_INCREMENT,
    first_name          VARCHAR(60)     NOT NULL,
    last_name           VARCHAR(60)     NOT NULL,
    gender              ENUM('MALE', 'FEMALE', 'OTHER') NOT NULL,
    dob                 DATE            NOT NULL,
    phone               VARCHAR(15)     NOT NULL,
    email               VARCHAR(100)    NULL,
    address             VARCHAR(255)    NOT NULL,
    blood_group         ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    emergency_contact   VARCHAR(15)     NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_patients PRIMARY KEY (patient_id),
    CONSTRAINT uq_patients_phone UNIQUE (phone),
    CONSTRAINT chk_patients_name CHECK (CHAR_LENGTH(first_name) >= 1)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 5. appointments  — N:1 patient, N:1 doctor
--    Double-booking of active slots is blocked by trigger (06_triggers.sql)
--    so a cancelled slot can be reused (a UNIQUE index would forbid that).
-- -----------------------------------------------------------------------------
CREATE TABLE appointments (
    appointment_id      INT             NOT NULL AUTO_INCREMENT,
    patient_id          INT             NOT NULL,
    doctor_id           INT             NOT NULL,
    appointment_date    DATE            NOT NULL,
    appointment_time    TIME            NOT NULL,
    status              ENUM('SCHEDULED', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'SCHEDULED',
    reason              VARCHAR(255)    NOT NULL DEFAULT 'General consultation',
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_appointments PRIMARY KEY (appointment_id),
    CONSTRAINT fk_appointments_patient
        FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_appointments_doctor
        FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_appointments_date CHECK (appointment_date >= '2020-01-01')
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 6. treatments  — 1:1 with a completed appointment
-- -----------------------------------------------------------------------------
CREATE TABLE treatments (
    treatment_id        INT             NOT NULL AUTO_INCREMENT,
    appointment_id      INT             NOT NULL,
    diagnosis           VARCHAR(255)    NOT NULL,
    prescription        TEXT            NOT NULL,
    treatment_notes     TEXT            NULL,
    treatment_charges   DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_treatments PRIMARY KEY (treatment_id),
    CONSTRAINT uq_treatments_appointment UNIQUE (appointment_id),
    CONSTRAINT fk_treatments_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_treatments_charges CHECK (treatment_charges >= 0)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 7. bills  — 1:1 with appointment; amounts stored (not derived at read time)
--    because GST rate can change historically. Totals are kept consistent
--    by GenerateBill() and the after-treatment trigger.
-- -----------------------------------------------------------------------------
CREATE TABLE bills (
    bill_id             INT             NOT NULL AUTO_INCREMENT,
    patient_id          INT             NOT NULL,
    appointment_id      INT             NOT NULL,
    consultation_fee    DECIMAL(10,2)   NOT NULL,
    treatment_charges   DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    gst_rate            DECIMAL(5,2)    NOT NULL DEFAULT 18.00,
    gst_amount          DECIMAL(10,2)   NOT NULL,
    total_amount        DECIMAL(10,2)   NOT NULL,
    status              ENUM('PENDING', 'PARTIAL', 'PAID') NOT NULL DEFAULT 'PENDING',
    generated_at        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_bills PRIMARY KEY (bill_id),
    CONSTRAINT uq_bills_appointment UNIQUE (appointment_id),
    CONSTRAINT fk_bills_patient
        FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_bills_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_bills_gst CHECK (gst_rate >= 0 AND gst_rate <= 28),
    CONSTRAINT chk_bills_total CHECK (total_amount >= 0)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 8. payments  — N:1 with bills (supports partial payments)
-- -----------------------------------------------------------------------------
CREATE TABLE payments (
    payment_id          INT             NOT NULL AUTO_INCREMENT,
    bill_id             INT             NOT NULL,
    amount              DECIMAL(10,2)   NOT NULL,
    payment_method      ENUM('CASH', 'CARD', 'UPI') NOT NULL,
    payment_date        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transaction_ref     VARCHAR(60)     NULL,
    recorded_by         INT             NULL,

    CONSTRAINT pk_payments PRIMARY KEY (payment_id),
    CONSTRAINT fk_payments_bill
        FOREIGN KEY (bill_id) REFERENCES bills (bill_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_payments_user
        FOREIGN KEY (recorded_by) REFERENCES users (user_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_payments_amount CHECK (amount > 0)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- payment_audit  — written by trg_audit_payment (not a core 3NF entity;
--                  it is an append-only log, so redundancy is intentional)
-- -----------------------------------------------------------------------------
CREATE TABLE payment_audit (
    audit_id            INT             NOT NULL AUTO_INCREMENT,
    payment_id          INT             NOT NULL,
    bill_id             INT             NOT NULL,
    amount              DECIMAL(10,2)   NOT NULL,
    payment_method      VARCHAR(10)     NOT NULL,
    action              VARCHAR(20)     NOT NULL DEFAULT 'INSERT',
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_payment_audit PRIMARY KEY (audit_id)
) ENGINE=InnoDB;
