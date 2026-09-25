-- =============================================================================
-- 05_procedures.sql
-- BookAppointment(), GenerateBill(), GetPatientHistory()
-- =============================================================================

USE hospital_db;

DROP PROCEDURE IF EXISTS BookAppointment;
DROP PROCEDURE IF EXISTS GenerateBill;
DROP PROCEDURE IF EXISTS GetPatientHistory;

DELIMITER $$

-- Book a slot after checking doctor hours and active double-booking.
CREATE PROCEDURE BookAppointment(
    IN  p_patient_id   INT,
    IN  p_doctor_id    INT,
    IN  p_date         DATE,
    IN  p_time         TIME,
    IN  p_reason       VARCHAR(255),
    OUT p_appointment_id INT,
    OUT p_message      VARCHAR(255)
)
BEGIN
    DECLARE v_from TIME;
    DECLARE v_to   TIME;
    DECLARE v_available TINYINT;
    DECLARE v_clash INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_appointment_id = NULL;
        SET p_message = 'Booking failed because of a database error.';
    END;

    START TRANSACTION;

    SELECT available_from, available_to, is_available
      INTO v_from, v_to, v_available
    FROM doctors
    WHERE doctor_id = p_doctor_id
    FOR UPDATE;

    IF v_from IS NULL THEN
        SET p_message = 'Doctor not found.';
        SET p_appointment_id = NULL;
        ROLLBACK;
    ELSEIF v_available = 0 THEN
        SET p_message = 'Doctor is marked unavailable.';
        SET p_appointment_id = NULL;
        ROLLBACK;
    ELSEIF p_time < v_from OR p_time >= v_to THEN
        SET p_message = 'Requested time is outside the doctor''s hours.';
        SET p_appointment_id = NULL;
        ROLLBACK;
    ELSE
        SELECT COUNT(*) INTO v_clash
        FROM appointments
        WHERE doctor_id = p_doctor_id
          AND appointment_date = p_date
          AND appointment_time = p_time
          AND status <> 'CANCELLED';

        IF v_clash > 0 THEN
            SET p_message = 'Slot already booked for this doctor.';
            SET p_appointment_id = NULL;
            ROLLBACK;
        ELSE
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason)
            VALUES (p_patient_id, p_doctor_id, p_date, p_time, IFNULL(p_reason, 'General consultation'));

            SET p_appointment_id = LAST_INSERT_ID();
            SET p_message = 'Appointment booked.';
            COMMIT;
        END IF;
    END IF;
END$$

-- Build a bill from the doctor's fee + any treatment charges + GST.
CREATE PROCEDURE GenerateBill(
    IN  p_appointment_id INT,
    IN  p_gst_rate       DECIMAL(5,2),
    OUT p_bill_id        INT,
    OUT p_message        VARCHAR(255)
)
BEGIN
    DECLARE v_patient_id INT;
    DECLARE v_status     VARCHAR(20);
    DECLARE v_fee        DECIMAL(10,2);
    DECLARE v_charges    DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_gst        DECIMAL(10,2);
    DECLARE v_total      DECIMAL(10,2);
    DECLARE v_exists     INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_bill_id = NULL;
        SET p_message = 'Bill generation failed.';
    END;

    START TRANSACTION;

    SELECT a.patient_id, a.status, d.consultation_fee
      INTO v_patient_id, v_status, v_fee
    FROM appointments a
    JOIN doctors d ON d.doctor_id = a.doctor_id
    WHERE a.appointment_id = p_appointment_id
    FOR UPDATE;

    IF v_patient_id IS NULL THEN
        SET p_message = 'Appointment not found.';
        SET p_bill_id = NULL;
        ROLLBACK;
    ELSEIF v_status <> 'COMPLETED' THEN
        SET p_message = 'Bill can be generated only for completed appointments.';
        SET p_bill_id = NULL;
        ROLLBACK;
    ELSE
        SELECT COUNT(*) INTO v_exists FROM bills WHERE appointment_id = p_appointment_id;
        IF v_exists > 0 THEN
            SET p_message = 'A bill already exists for this appointment.';
            SELECT bill_id INTO p_bill_id FROM bills WHERE appointment_id = p_appointment_id;
            ROLLBACK;
        ELSE
            SELECT IFNULL(treatment_charges, 0) INTO v_charges
            FROM treatments
            WHERE appointment_id = p_appointment_id;

            SET v_gst   = ROUND((v_fee + IFNULL(v_charges, 0)) * (p_gst_rate / 100), 2);
            SET v_total = ROUND(v_fee + IFNULL(v_charges, 0) + v_gst, 2);

            INSERT INTO bills (
                patient_id, appointment_id, consultation_fee, treatment_charges,
                gst_rate, gst_amount, total_amount, status
            ) VALUES (
                v_patient_id, p_appointment_id, v_fee, IFNULL(v_charges, 0),
                p_gst_rate, v_gst, v_total, 'PENDING'
            );

            SET p_bill_id = LAST_INSERT_ID();
            SET p_message = 'Bill generated.';
            COMMIT;
        END IF;
    END IF;
END$$

-- Return the patient_history view for one patient.
CREATE PROCEDURE GetPatientHistory(IN p_patient_id INT)
BEGIN
    SELECT *
    FROM patient_history
    WHERE patient_id = p_patient_id
    ORDER BY appointment_date DESC, appointment_time DESC;
END$$

DELIMITER ;
