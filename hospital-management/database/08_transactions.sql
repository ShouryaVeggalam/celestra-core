-- =============================================================================
-- 08_transactions.sql
-- Demonstrates BEGIN / COMMIT / ROLLBACK and the ACID properties.
--
-- ACID (why transactions exist)
-- -----------------------------
-- A  Atomicity     All statements in the transaction succeed, or none do.
--                  Here: if the payment insert fails, the bill status is
--                  not left half-updated.
-- C  Consistency   Constraints (FK, CHECK, UNIQUE) still hold after COMMIT.
--                  A payment can never reference a missing bill.
-- I  Isolation     Concurrent sessions do not see each other's uncommitted
--                  work. FOR UPDATE locks the bill row so two cashiers
--                  cannot over-pay the same bill at once.
-- D  Durability    After COMMIT, MySQL has flushed the change to the
--                  InnoDB redo log; a crash will not lose the payment.
-- =============================================================================

USE hospital_db;

-- ---------------------------------------------------------------------------
-- Scenario A — COMMIT
-- Record a payment and (via the audit trigger) mark the bill PAID/PARTIAL.
-- ---------------------------------------------------------------------------
START TRANSACTION;

    -- Lock the pending bill for patient 17 (bill_id 17, total 1121.00)
    SELECT bill_id, total_amount, status
    FROM bills
    WHERE bill_id = 17
    FOR UPDATE;

    INSERT INTO payments (bill_id, amount, payment_method, transaction_ref, recorded_by)
    VALUES (17, 1121.00, 'UPI', 'TXN-ACID-COMMIT', 2);

COMMIT;

-- Verify: bill 17 should now be PAID and an audit row should exist.
SELECT bill_id, status FROM bills WHERE bill_id = 17;
SELECT * FROM payment_audit WHERE transaction_ref IS NULL AND payment_id = LAST_INSERT_ID()
UNION
SELECT pa.* FROM payment_audit pa
JOIN payments p ON p.payment_id = pa.payment_id
WHERE p.transaction_ref = 'TXN-ACID-COMMIT';


-- ---------------------------------------------------------------------------
-- Scenario B — ROLLBACK
-- Start a payment, then abort. Nothing durable is written.
-- ---------------------------------------------------------------------------
START TRANSACTION;

    INSERT INTO payments (bill_id, amount, payment_method, transaction_ref, recorded_by)
    VALUES (15, 500.00, 'CASH', 'TXN-ACID-ROLLBACK', 2);

    -- Imagine the card machine timed out:
ROLLBACK;

-- Verify: no payment with this reference, bill 15 still PENDING.
SELECT COUNT(*) AS rolled_back_rows
FROM payments
WHERE transaction_ref = 'TXN-ACID-ROLLBACK';

SELECT bill_id, status FROM bills WHERE bill_id = 15;


-- ---------------------------------------------------------------------------
-- Scenario C — Atomic booking (two statements, one outcome)
-- Insert appointment + immediately generate a placeholder note, then
-- roll back to prove neither row survives.
-- ---------------------------------------------------------------------------
START TRANSACTION;

    INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason)
    VALUES (2, 5, '2026-12-31', '10:00:00', 'ACID demo — must not persist');

    -- Savepoint lets us undo only the second statement if needed
    SAVEPOINT after_appointment;

    -- This would fail CHECK (amount > 0) if we tried a zero payment —
    -- demonstrating Consistency. We roll back the whole transaction instead.
ROLLBACK TO SAVEPOINT after_appointment;
ROLLBACK;

SELECT COUNT(*) AS leaked_demo_rows
FROM appointments
WHERE reason LIKE 'ACID demo%';
