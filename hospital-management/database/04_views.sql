-- =============================================================================
-- 04_views.sql
-- Views hide join complexity from the application / viva demo.
-- =============================================================================

USE hospital_db;

DROP VIEW IF EXISTS patient_history;
DROP VIEW IF EXISTS doctor_schedule;
DROP VIEW IF EXISTS pending_bills;

-- Full clinical + billing trail for one patient (filter by patient_id)
CREATE VIEW patient_history AS
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name)              AS patient_name,
    p.phone,
    p.blood_group,
    a.appointment_id,
    a.appointment_date,
    a.appointment_time,
    a.status                                            AS appointment_status,
    CONCAT(d.first_name, ' ', d.last_name)              AS doctor_name,
    dep.name                                            AS department,
    t.diagnosis,
    t.prescription,
    t.treatment_notes,
    b.bill_id,
    b.total_amount,
    b.status                                            AS bill_status
FROM patients p
LEFT JOIN appointments a ON a.patient_id = p.patient_id
LEFT JOIN doctors d      ON d.doctor_id = a.doctor_id
LEFT JOIN departments dep ON dep.department_id = d.department_id
LEFT JOIN treatments t   ON t.appointment_id = a.appointment_id
LEFT JOIN bills b        ON b.appointment_id = a.appointment_id;

-- Who is booked, when, and whether the slot is still active
CREATE VIEW doctor_schedule AS
SELECT
    d.doctor_id,
    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
    dep.name                               AS department,
    d.available_from,
    d.available_to,
    a.appointment_id,
    a.appointment_date,
    a.appointment_time,
    a.status,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.phone                                AS patient_phone
FROM doctors d
JOIN departments dep ON dep.department_id = d.department_id
LEFT JOIN appointments a ON a.doctor_id = d.doctor_id
LEFT JOIN patients p     ON p.patient_id = a.patient_id;

-- Reception desk: bills that still have money outstanding
CREATE VIEW pending_bills AS
SELECT
    b.bill_id,
    b.appointment_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.phone,
    b.consultation_fee,
    b.treatment_charges,
    b.gst_amount,
    b.total_amount,
    IFNULL(SUM(pay.amount), 0)             AS amount_paid,
    b.total_amount - IFNULL(SUM(pay.amount), 0) AS outstanding,
    b.status,
    b.generated_at
FROM bills b
JOIN patients p ON p.patient_id = b.patient_id
LEFT JOIN payments pay ON pay.bill_id = b.bill_id
WHERE b.status IN ('PENDING', 'PARTIAL')
GROUP BY
    b.bill_id, b.appointment_id, p.first_name, p.last_name, p.phone,
    b.consultation_fee, b.treatment_charges, b.gst_amount,
    b.total_amount, b.status, b.generated_at;
