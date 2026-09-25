-- =============================================================================
-- 03_queries.sql  —  25 queries covering the DBMS syllabus
-- SELECT, WHERE, ORDER BY, GROUP BY, HAVING,
-- INNER JOIN, LEFT JOIN, SELF JOIN, SUBQUERY, AGGREGATES
-- =============================================================================

USE hospital_db;

-- Q01  SELECT: list every department
SELECT department_id, name, floor
FROM departments;

-- Q02  WHERE: female patients with blood group O+
SELECT patient_id, first_name, last_name, phone
FROM patients
WHERE gender = 'FEMALE' AND blood_group = 'O+';

-- Q03  ORDER BY: doctors by consultation fee (highest first)
SELECT doctor_id, first_name, last_name, consultation_fee
FROM doctors
ORDER BY consultation_fee DESC;

-- Q04  GROUP BY + COUNT: patients per blood group
SELECT blood_group, COUNT(*) AS patient_count
FROM patients
GROUP BY blood_group
ORDER BY patient_count DESC;

-- Q05  GROUP BY + HAVING: departments with more than one doctor
SELECT d.name, COUNT(doc.doctor_id) AS doctor_count
FROM departments d
JOIN doctors doc ON doc.department_id = d.department_id
GROUP BY d.department_id, d.name
HAVING COUNT(doc.doctor_id) > 1;

-- Q06  INNER JOIN: appointments with patient and doctor names
SELECT
    a.appointment_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient,
    CONCAT(doc.first_name, ' ', doc.last_name) AS doctor,
    a.appointment_date,
    a.status
FROM appointments a
INNER JOIN patients p  ON p.patient_id = a.patient_id
INNER JOIN doctors  doc ON doc.doctor_id = a.doctor_id
ORDER BY a.appointment_date;

-- Q07  LEFT JOIN: every doctor and how many appointments they have
--     (doctors with zero appointments still appear)
SELECT
    CONCAT(doc.first_name, ' ', doc.last_name) AS doctor,
    COUNT(a.appointment_id) AS appointment_count
FROM doctors doc
LEFT JOIN appointments a ON a.doctor_id = doc.doctor_id
GROUP BY doc.doctor_id, doc.first_name, doc.last_name;

-- Q08  LEFT JOIN: patients who have never had a bill
SELECT p.patient_id, p.first_name, p.last_name
FROM patients p
LEFT JOIN bills b ON b.patient_id = p.patient_id
WHERE b.bill_id IS NULL;

-- Q09  SELF JOIN: pairs of doctors who work in the same department
SELECT
    CONCAT(d1.first_name, ' ', d1.last_name) AS doctor_a,
    CONCAT(d2.first_name, ' ', d2.last_name) AS doctor_b,
    dep.name AS department
FROM doctors d1
INNER JOIN doctors d2
    ON d1.department_id = d2.department_id
   AND d1.doctor_id < d2.doctor_id
INNER JOIN departments dep ON dep.department_id = d1.department_id;

-- Q10  SUBQUERY (scalar): doctors earning more than the average fee
SELECT first_name, last_name, consultation_fee
FROM doctors
WHERE consultation_fee > (SELECT AVG(consultation_fee) FROM doctors);

-- Q11  SUBQUERY (IN): patients who visited Cardiology
SELECT first_name, last_name, phone
FROM patients
WHERE patient_id IN (
    SELECT a.patient_id
    FROM appointments a
    JOIN doctors d ON d.doctor_id = a.doctor_id
    JOIN departments dep ON dep.department_id = d.department_id
    WHERE dep.name = 'Cardiology'
);

-- Q12  SUBQUERY (EXISTS): doctors who have at least one completed visit
SELECT first_name, last_name
FROM doctors d
WHERE EXISTS (
    SELECT 1 FROM appointments a
    WHERE a.doctor_id = d.doctor_id AND a.status = 'COMPLETED'
);

-- Q13  AGGREGATE SUM: total hospital revenue from paid / partial bills
SELECT SUM(total_amount) AS billed_total,
       SUM(CASE WHEN status = 'PAID' THEN total_amount ELSE 0 END) AS collected_potential
FROM bills;

-- Q14  AGGREGATE AVG / MIN / MAX: consultation fee statistics
SELECT
    MIN(consultation_fee) AS lowest_fee,
    MAX(consultation_fee) AS highest_fee,
    ROUND(AVG(consultation_fee), 2) AS average_fee
FROM doctors;

-- Q15  Monthly revenue (GROUP BY year-month) — used by the dashboard chart
SELECT
    DATE_FORMAT(generated_at, '%Y-%m') AS month,
    ROUND(SUM(total_amount), 2) AS revenue
FROM bills
GROUP BY DATE_FORMAT(generated_at, '%Y-%m')
ORDER BY month;

-- Q16  Department-wise patient count (distinct patients)
SELECT
    dep.name AS department,
    COUNT(DISTINCT a.patient_id) AS unique_patients
FROM departments dep
JOIN doctors d ON d.department_id = dep.department_id
JOIN appointments a ON a.doctor_id = d.doctor_id
GROUP BY dep.department_id, dep.name
ORDER BY unique_patients DESC;

-- Q17  Pending / partial bills with outstanding amount
SELECT
    b.bill_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient,
    b.total_amount,
    IFNULL(SUM(pay.amount), 0) AS paid,
    b.total_amount - IFNULL(SUM(pay.amount), 0) AS outstanding
FROM bills b
JOIN patients p ON p.patient_id = b.patient_id
LEFT JOIN payments pay ON pay.bill_id = b.bill_id
WHERE b.status IN ('PENDING', 'PARTIAL')
GROUP BY b.bill_id, p.first_name, p.last_name, b.total_amount;

-- Q18  Today's appointments
SELECT a.appointment_id, a.appointment_time, a.status,
       CONCAT(p.first_name, ' ', p.last_name) AS patient,
       CONCAT(d.first_name, ' ', d.last_name) AS doctor
FROM appointments a
JOIN patients p ON p.patient_id = a.patient_id
JOIN doctors d  ON d.doctor_id  = a.doctor_id
WHERE a.appointment_date = CURDATE()
ORDER BY a.appointment_time;

-- Q19  BETWEEN / LIKE: patients whose name starts with 'A' born after 1980
SELECT first_name, last_name, dob
FROM patients
WHERE first_name LIKE 'A%'
  AND dob BETWEEN '1980-01-01' AND '2005-12-31';

-- Q20  LIMIT: top 5 highest bills
SELECT bill_id, total_amount, status
FROM bills
ORDER BY total_amount DESC
LIMIT 5;

-- Q21  CASE expression: classify appointments
SELECT appointment_id, status,
       CASE
           WHEN status = 'SCHEDULED' THEN 'Upcoming'
           WHEN status = 'COMPLETED' THEN 'Closed'
           ELSE 'Dropped'
       END AS bucket
FROM appointments;

-- Q22  Nested aggregate: department whose doctors have the highest average fee
SELECT name FROM departments
WHERE department_id = (
    SELECT department_id
    FROM doctors
    GROUP BY department_id
    ORDER BY AVG(consultation_fee) DESC
    LIMIT 1
);

-- Q23  JOIN treatments: diagnosis history for a given patient (Rahul Verma = 1)
SELECT
    a.appointment_date,
    t.diagnosis,
    t.prescription,
    CONCAT(d.first_name, ' ', d.last_name) AS doctor
FROM treatments t
JOIN appointments a ON a.appointment_id = t.appointment_id
JOIN doctors d ON d.doctor_id = a.doctor_id
WHERE a.patient_id = 1
ORDER BY a.appointment_date DESC;

-- Q24  UNION: contact directory of doctors and patients
SELECT 'DOCTOR' AS kind, first_name, last_name, phone FROM doctors
UNION
SELECT 'PATIENT', first_name, last_name, phone FROM patients
ORDER BY kind, first_name;

-- Q25  Correlated subquery: each bill vs the average bill of that month
SELECT
    bill_id,
    DATE_FORMAT(generated_at, '%Y-%m') AS month,
    total_amount,
    (
        SELECT ROUND(AVG(b2.total_amount), 2)
        FROM bills b2
        WHERE DATE_FORMAT(b2.generated_at, '%Y-%m') = DATE_FORMAT(b1.generated_at, '%Y-%m')
    ) AS month_average
FROM bills b1
ORDER BY generated_at;
