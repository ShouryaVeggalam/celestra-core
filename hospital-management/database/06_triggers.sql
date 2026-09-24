-- =============================================================================
-- 06_triggers.sql
-- 1. Prevent duplicate (active) appointments
-- 2. Recalculate the bill after a treatment is added / updated
-- 3. Audit every payment insert and refresh bill status
-- =============================================================================

USE hospital_db;

DROP TRIGGER IF EXISTS trg_prevent_duplicate_appointment;
DROP TRIGGER IF EXISTS trg_update_bill_after_treatment;
DROP TRIGGER IF EXISTS trg_update_bill_after_treatment_upd;
DROP TRIGGER IF EXISTS trg_audit_payment;

DELIMITER $$

-- Fired BEFORE INSERT so a clashing SCHEDULED/COMPLETED slot is rejected.
-- CANCELLED rows are ignored, which lets reception re-book the same slot.
CREATE TRIGGER trg_prevent_duplicate_appointment
BEFORE INSERT ON appointments
FOR EACH ROW
BEGIN
    DECLARE v_count INT DEFAULT 0;

    SELECT COUNT(*) INTO v_count
    FROM appointments
    WHERE doctor_id = NEW.doctor_id
      AND appointment_date = NEW.appointment_date
      AND appointment_time = NEW.appointment_time
      AND status <> 'CANCELLED';

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Duplicate appointment: doctor already booked at this date and time.';
    END IF;
END$$

-- When a treatment is recorded, push charges onto an existing bill (if any)
-- and recompute GST + total. If no bill exists yet, GenerateBill() will pick
-- the charges up later.
CREATE TRIGGER trg_update_bill_after_treatment
AFTER INSERT ON treatments
FOR EACH ROW
BEGIN
    UPDATE bills
    SET treatment_charges = NEW.treatment_charges,
        gst_amount = ROUND((consultation_fee + NEW.treatment_charges) * (gst_rate / 100), 2),
        total_amount = ROUND(
            consultation_fee + NEW.treatment_charges
            + ROUND((consultation_fee + NEW.treatment_charges) * (gst_rate / 100), 2)
        , 2)
    WHERE appointment_id = NEW.appointment_id;
END$$

CREATE TRIGGER trg_update_bill_after_treatment_upd
AFTER UPDATE ON treatments
FOR EACH ROW
BEGIN
    UPDATE bills
    SET treatment_charges = NEW.treatment_charges,
        gst_amount = ROUND((consultation_fee + NEW.treatment_charges) * (gst_rate / 100), 2),
        total_amount = ROUND(
            consultation_fee + NEW.treatment_charges
            + ROUND((consultation_fee + NEW.treatment_charges) * (gst_rate / 100), 2)
        , 2)
    WHERE appointment_id = NEW.appointment_id;
END$$

-- Append-only audit row + roll payment totals into bill.status
CREATE TRIGGER trg_audit_payment
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    DECLARE v_total DECIMAL(10,2);
    DECLARE v_paid  DECIMAL(10,2);

    INSERT INTO payment_audit (payment_id, bill_id, amount, payment_method, action)
    VALUES (NEW.payment_id, NEW.bill_id, NEW.amount, NEW.payment_method, 'INSERT');

    SELECT total_amount INTO v_total FROM bills WHERE bill_id = NEW.bill_id;
    SELECT IFNULL(SUM(amount), 0) INTO v_paid FROM payments WHERE bill_id = NEW.bill_id;

    IF v_paid >= v_total THEN
        UPDATE bills SET status = 'PAID' WHERE bill_id = NEW.bill_id;
    ELSEIF v_paid > 0 THEN
        UPDATE bills SET status = 'PARTIAL' WHERE bill_id = NEW.bill_id;
    END IF;
END$$

DELIMITER ;
