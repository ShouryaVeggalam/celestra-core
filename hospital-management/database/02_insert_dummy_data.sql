-- =============================================================================
-- 02_insert_dummy_data.sql
-- Demo logins (bcrypt):
--   admin         / Admin@123
--   receptionist  / Reception@123
--   dr.arjun      / Doctor@123   (same password for every doctor account)
-- =============================================================================

USE hospital_db;

-- ---------------------------------------------------------------------------
-- Users (1 admin + 1 receptionist + 8 doctors)
-- ---------------------------------------------------------------------------
INSERT INTO users (username, email, password_hash, role) VALUES
('admin',        'admin@celestra.hospital',        '$2b$10$92eKi9UX93nLFjtEMPlMuO8OKeQBPhgNuLVXT9VDVhHVm.CgQ.l1G', 'ADMIN'),
('receptionist', 'reception@celestra.hospital',    '$2b$10$7v6nOMrECwrg9g2Om29m.ObCjQUnkpXWZuBNfBXG0RSuOvnOJ.V4m', 'RECEPTIONIST'),
('dr.arjun',     'arjun.mehta@celestra.hospital',  '$2b$10$nqxNyLTKAyW.BLLUVeEtcO3THtW5H5rsV16rFKve3OKytJe6UXa3m', 'DOCTOR'),
('dr.priya',     'priya.sharma@celestra.hospital', '$2b$10$nqxNyLTKAyW.BLLUVeEtcO3THtW5H5rsV16rFKve3OKytJe6UXa3m', 'DOCTOR'),
('dr.rohan',     'rohan.kapoor@celestra.hospital', '$2b$10$nqxNyLTKAyW.BLLUVeEtcO3THtW5H5rsV16rFKve3OKytJe6UXa3m', 'DOCTOR'),
('dr.ananya',    'ananya.iyer@celestra.hospital',  '$2b$10$nqxNyLTKAyW.BLLUVeEtcO3THtW5H5rsV16rFKve3OKytJe6UXa3m', 'DOCTOR'),
('dr.vikram',    'vikram.singh@celestra.hospital', '$2b$10$nqxNyLTKAyW.BLLUVeEtcO3THtW5H5rsV16rFKve3OKytJe6UXa3m', 'DOCTOR'),
('dr.sneha',     'sneha.reddy@celestra.hospital',  '$2b$10$nqxNyLTKAyW.BLLUVeEtcO3THtW5H5rsV16rFKve3OKytJe6UXa3m', 'DOCTOR'),
('dr.karan',     'karan.malhotra@celestra.hospital','$2b$10$nqxNyLTKAyW.BLLUVeEtcO3THtW5H5rsV16rFKve3OKytJe6UXa3m', 'DOCTOR'),
('dr.meera',     'meera.nair@celestra.hospital',   '$2b$10$nqxNyLTKAyW.BLLUVeEtcO3THtW5H5rsV16rFKve3OKytJe6UXa3m', 'DOCTOR');

-- ---------------------------------------------------------------------------
-- 5 Departments
-- ---------------------------------------------------------------------------
INSERT INTO departments (name, description, floor) VALUES
('Cardiology',        'Heart and vascular care',                 '2'),
('Neurology',         'Brain, spine and nerve disorders',        '3'),
('Orthopedics',       'Bones, joints and sports injuries',       '1'),
('Pediatrics',        'Child and adolescent medicine',           '4'),
('General Medicine',  'Primary care and internal medicine',      '1');

-- ---------------------------------------------------------------------------
-- 8 Doctors  (user_id 3..10 map to the doctor accounts above)
-- ---------------------------------------------------------------------------
INSERT INTO doctors
    (user_id, department_id, first_name, last_name, specialization, qualification, phone, available_from, available_to, consultation_fee)
VALUES
(3,  1, 'Arjun',  'Mehta',    'Interventional Cardiology', 'DM Cardiology',     '9810000001', '09:00:00', '17:00:00', 1200.00),
(4,  2, 'Priya',  'Sharma',   'Clinical Neurology',        'DM Neurology',      '9810000002', '10:00:00', '18:00:00', 1100.00),
(5,  3, 'Rohan',  'Kapoor',   'Joint Replacement',         'MS Orthopedics',    '9810000003', '08:00:00', '16:00:00',  900.00),
(6,  4, 'Ananya', 'Iyer',     'Pediatric Care',            'MD Pediatrics',     '9810000004', '09:00:00', '15:00:00',  700.00),
(7,  5, 'Vikram', 'Singh',    'Internal Medicine',         'MD General Med',    '9810000005', '09:00:00', '17:00:00',  500.00),
(8,  1, 'Sneha',  'Reddy',    'Non-invasive Cardiology',   'DM Cardiology',     '9810000006', '11:00:00', '19:00:00', 1000.00),
(9,  3, 'Karan',  'Malhotra', 'Sports Medicine',           'MS Orthopedics',    '9810000007', '08:30:00', '14:30:00',  850.00),
(10, 2, 'Meera',  'Nair',     'Stroke Medicine',           'DM Neurology',      '9810000008', '12:00:00', '20:00:00', 1150.00);

-- ---------------------------------------------------------------------------
-- 20 Patients
-- ---------------------------------------------------------------------------
INSERT INTO patients
    (first_name, last_name, gender, dob, phone, email, address, blood_group, emergency_contact)
VALUES
('Rahul',     'Verma',     'MALE',   '1988-03-12', '9900000001', 'rahul.verma@mail.com',     '12 MG Road, Bengaluru',          'O+',  '9900000101'),
('Kavya',     'Nair',      'FEMALE', '1994-07-21', '9900000002', 'kavya.nair@mail.com',      '44 Marine Drive, Kochi',         'A+',  '9900000102'),
('Amit',      'Patel',     'MALE',   '1979-11-05', '9900000003', 'amit.patel@mail.com',      '8 CG Road, Ahmedabad',           'B+',  '9900000103'),
('Sana',      'Khan',      'FEMALE', '2001-01-18', '9900000004', 'sana.khan@mail.com',       '21 Park Street, Kolkata',        'O-',  '9900000104'),
('Dev',       'Joshi',     'MALE',   '1965-09-30', '9900000005', 'dev.joshi@mail.com',       '5 FC Road, Pune',                'AB+', '9900000105'),
('Nisha',     'Gupta',     'FEMALE', '1990-04-09', '9900000006', 'nisha.gupta@mail.com',     '33 Connaught Place, Delhi',      'A-',  '9900000106'),
('Farhan',    'Ali',       'MALE',   '1982-12-02', '9900000007', 'farhan.ali@mail.com',      '90 Banjara Hills, Hyderabad',    'B-',  '9900000107'),
('Meenal',    'Desai',     'FEMALE', '1973-06-14', '9900000008', 'meenal.desai@mail.com',    '16 Law Garden, Ahmedabad',       'O+',  '9900000108'),
('Ishaan',    'Reddy',     'MALE',   '2016-08-25', '9900000009', 'ishaan.reddy@mail.com',    '7 Jubilee Hills, Hyderabad',     'A+',  '9900000109'),
('Pooja',     'Mishra',    'FEMALE', '1998-02-11', '9900000010', 'pooja.mishra@mail.com',    '4 Hazratganj, Lucknow',          'B+',  '9900000110'),
('Arun',      'Pillai',    'MALE',   '1958-05-19', '9900000011', 'arun.pillai@mail.com',     '11 Kowdiar, Thiruvananthapuram', 'O+',  '9900000111'),
('Tanya',     'Bose',      'FEMALE', '1986-10-07', '9900000012', 'tanya.bose@mail.com',      '28 Salt Lake, Kolkata',          'AB-', '9900000112'),
('Harsh',     'Agarwal',   'MALE',   '1992-03-28', '9900000013', 'harsh.agarwal@mail.com',   '19 Civil Lines, Jaipur',         'A+',  '9900000113'),
('Leela',     'Menon',     'FEMALE', '1969-12-22', '9900000014', 'leela.menon@mail.com',     '3 Panampilly Nagar, Kochi',      'O-',  '9900000114'),
('Yusuf',     'Sheikh',    'MALE',   '2004-09-01', '9900000015', 'yusuf.sheikh@mail.com',    '52 Lalbagh, Srinagar',           'B+',  '9900000115'),
('Ritu',      'Chawla',    'FEMALE', '1984-07-16', '9900000016', 'ritu.chawla@mail.com',     '8 Sector 17, Chandigarh',        'A+',  '9900000116'),
('Nikhil',    'Rao',       'MALE',   '1977-01-03', '9900000017', 'nikhil.rao@mail.com',      '14 Indiranagar, Bengaluru',      'O+',  '9900000117'),
('Aisha',     'Qureshi',   'FEMALE', '1996-11-27', '9900000018', 'aisha.qureshi@mail.com',   '6 Charminar Road, Hyderabad',    'B-',  '9900000118'),
('Soren',     'Dutta',     'MALE',   '2012-04-04', '9900000019', 'soren.dutta@mail.com',     '25 Gariahat, Kolkata',           'A-',  '9900000119'),
('Gauri',     'Kulkarni',  'FEMALE', '1961-08-08', '9900000020', 'gauri.kulkarni@mail.com',  '9 Koregaon Park, Pune',          'AB+', '9900000120');

-- ---------------------------------------------------------------------------
-- 30 Appointments  (mix of SCHEDULED / COMPLETED / CANCELLED)
-- Dates span the current academic year so dashboard "today" still works after
-- seed; completed visits sit in past months for revenue charts.
-- ---------------------------------------------------------------------------
INSERT INTO appointments
    (patient_id, doctor_id, appointment_date, appointment_time, status, reason)
VALUES
-- Completed (used for treatments + bills)
(1,  1, '2026-01-10', '10:00:00', 'COMPLETED', 'Chest pain evaluation'),
(2,  2, '2026-01-12', '11:00:00', 'COMPLETED', 'Migraine follow-up'),
(3,  3, '2026-01-15', '09:30:00', 'COMPLETED', 'Knee pain'),
(4,  4, '2026-01-18', '10:30:00', 'COMPLETED', 'Fever and cough'),
(5,  5, '2026-02-03', '09:00:00', 'COMPLETED', 'Annual checkup'),
(6,  6, '2026-02-08', '12:00:00', 'COMPLETED', 'Palpitations'),
(7,  7, '2026-02-14', '09:00:00', 'COMPLETED', 'Shoulder injury'),
(8,  8, '2026-02-20', '13:00:00', 'COMPLETED', 'Dizziness'),
(9,  4, '2026-03-02', '11:00:00', 'COMPLETED', 'Vaccination review'),
(10, 1, '2026-03-11', '10:00:00', 'COMPLETED', 'Hypertension review'),
(11, 5, '2026-03-22', '14:00:00', 'COMPLETED', 'Diabetes follow-up'),
(12, 2, '2026-04-05', '11:30:00', 'COMPLETED', 'Seizure history'),
(13, 3, '2026-04-16', '08:30:00', 'COMPLETED', 'Back pain'),
(14, 6, '2026-05-07', '12:30:00', 'COMPLETED', 'ECG review'),
(15, 8, '2026-05-19', '15:00:00', 'COMPLETED', 'Headache'),
(16, 7, '2026-06-04', '10:00:00', 'COMPLETED', 'Ankle sprain'),
(17, 5, '2026-06-21', '11:00:00', 'COMPLETED', 'Fatigue'),
(18, 1, '2026-07-09', '09:30:00', 'COMPLETED', 'Breathlessness'),
(19, 4, '2026-07-22', '10:00:00', 'COMPLETED', 'Growth checkup'),
(20, 3, '2026-08-06', '09:00:00', 'COMPLETED', 'Hip stiffness'),
-- Cancelled (slot reusable)
(1,  2, '2026-08-12', '11:00:00', 'CANCELLED', 'Second opinion'),
(3,  6, '2026-08-18', '13:00:00', 'CANCELLED', 'Echo test'),
-- Upcoming / today-ish scheduled
(5,  1, '2026-09-03', '10:00:00', 'SCHEDULED', 'Post-op review'),
(7,  5, '2026-09-03', '11:00:00', 'SCHEDULED', 'Medication refill'),
(8,  8, '2026-09-04', '14:00:00', 'SCHEDULED', 'Stroke clinic'),
(10, 6, '2026-09-05', '12:00:00', 'SCHEDULED', 'BP monitoring'),
(12, 7, '2026-09-08', '09:00:00', 'SCHEDULED', 'Physio plan'),
(14, 2, '2026-09-10', '16:00:00', 'SCHEDULED', 'Nerve conduction'),
(16, 3, '2026-09-12', '10:30:00', 'SCHEDULED', 'Fracture follow-up'),
(18, 4, '2026-09-15', '11:30:00', 'SCHEDULED', 'Pediatric consult');

-- ---------------------------------------------------------------------------
-- 20 Treatments (one per completed appointment)
-- ---------------------------------------------------------------------------
INSERT INTO treatments (appointment_id, diagnosis, prescription, treatment_notes, treatment_charges)
VALUES
(1,  'Stable angina',              'Aspirin 75mg OD, Atorvastatin 10mg HS',          'Advise stress test if pain recurs',     2500.00),
(2,  'Migraine without aura',      'Naproxen 250mg SOS, Propranolol 20mg OD',        'Sleep hygiene counselling done',        800.00),
(3,  'Osteoarthritis knee',        'Aceclofenac 100mg BD, physiotherapy',            'X-ray suggested',                       1500.00),
(4,  'Viral upper respiratory',    'Paracetamol 250mg TDS, rest and fluids',         'No antibiotics required',               400.00),
(5,  'Essential hypertension',     'Amlodipine 5mg OD',                              'Lifestyle modification advised',        600.00),
(6,  'Sinus tachycardia',          'Metoprolol 25mg OD',                             'Holter if symptoms persist',            1800.00),
(7,  'Rotator cuff strain',        'Ice, NSAIDs, sling for 5 days',                  'Refer physio',                          1200.00),
(8,  'Benign positional vertigo',  'Betahistine 16mg TDS, canalith repositioning',   'Epley manoeuvre performed',             900.00),
(9,  'Healthy child',              'Vitamin D 400 IU OD',                            'Immunisation up to date',               300.00),
(10, 'Hypertension uncontrolled',  'Telmisartan 40mg OD',                            'Home BP chart for 2 weeks',             700.00),
(11, 'Type 2 diabetes mellitus',   'Metformin 500mg BD',                             'HbA1c in 3 months',                    650.00),
(12, 'Focal epilepsy',             'Levetiracetam 500mg BD',                         'Avoid sleep deprivation',               2200.00),
(13, 'Lumbar spondylosis',         'Tizanidine 2mg HS, core exercises',              'MRI if red flags appear',               1400.00),
(14, 'LVH on ECG',                 'Continue antihypertensives, echo in 6 months',   'Salt restriction',                      1600.00),
(15, 'Tension headache',           'Ibuprofen 400mg SOS, relaxation',                'Screen for refractive error',           500.00),
(16, 'Grade 1 ankle sprain',       'RICE protocol, ankle brace',                     'Return to sport in 2 weeks',            1100.00),
(17, 'Iron deficiency',            'Ferrous sulfate 200mg BD',                       'Diet counselling',                      450.00),
(18, 'Bronchial asthma',           'Budesonide inhaler 200mcg BD',                   'Inhaler technique demonstrated',        900.00),
(19, 'Normal growth',              'Multivitamin syrup 5ml OD',                      'Next visit in 6 months',                250.00),
(20, 'Early osteoarthritis hip',   'Paracetamol 650mg TDS, walking aids',            'Weight reduction advised',              1300.00);

-- ---------------------------------------------------------------------------
-- 20 Bills  (GST 18% on consultation + treatment)
-- total = (consultation_fee + treatment_charges) * 1.18
-- ---------------------------------------------------------------------------
INSERT INTO bills
    (patient_id, appointment_id, consultation_fee, treatment_charges, gst_rate, gst_amount, total_amount, status, generated_at)
VALUES
(1,  1,  1200.00, 2500.00, 18.00,  666.00,  4366.00, 'PAID',    '2026-01-10 11:00:00'),
(2,  2,  1100.00,  800.00, 18.00,  342.00,  2242.00, 'PAID',    '2026-01-12 12:00:00'),
(3,  3,   900.00, 1500.00, 18.00,  432.00,  2832.00, 'PAID',    '2026-01-15 10:30:00'),
(4,  4,   700.00,  400.00, 18.00,  198.00,  1298.00, 'PAID',    '2026-01-18 11:30:00'),
(5,  5,   500.00,  600.00, 18.00,  198.00,  1298.00, 'PAID',    '2026-02-03 10:00:00'),
(6,  6,  1000.00, 1800.00, 18.00,  504.00,  3304.00, 'PAID',    '2026-02-08 13:00:00'),
(7,  7,   850.00, 1200.00, 18.00,  369.00,  2419.00, 'PAID',    '2026-02-14 10:00:00'),
(8,  8,  1150.00,  900.00, 18.00,  369.00,  2419.00, 'PAID',    '2026-02-20 14:00:00'),
(9,  9,   700.00,  300.00, 18.00,  180.00,  1180.00, 'PAID',    '2026-03-02 12:00:00'),
(10, 10, 1200.00,  700.00, 18.00,  342.00,  2242.00, 'PAID',    '2026-03-11 11:00:00'),
(11, 11,  500.00,  650.00, 18.00,  207.00,  1357.00, 'PAID',    '2026-03-22 15:00:00'),
(12, 12, 1100.00, 2200.00, 18.00,  594.00,  3894.00, 'PAID',    '2026-04-05 12:30:00'),
(13, 13,  900.00, 1400.00, 18.00,  414.00,  2714.00, 'PAID',    '2026-04-16 09:30:00'),
(14, 14, 1000.00, 1600.00, 18.00,  468.00,  3068.00, 'PARTIAL', '2026-05-07 13:30:00'),
(15, 15, 1150.00,  500.00, 18.00,  297.00,  1947.00, 'PENDING', '2026-05-19 16:00:00'),
(16, 16,  850.00, 1100.00, 18.00,  351.00,  2301.00, 'PAID',    '2026-06-04 11:00:00'),
(17, 17,  500.00,  450.00, 18.00,  171.00,  1121.00, 'PENDING', '2026-06-21 12:00:00'),
(18, 18, 1200.00,  900.00, 18.00,  378.00,  2478.00, 'PAID',    '2026-07-09 10:30:00'),
(19, 19,  700.00,  250.00, 18.00,  171.00,  1121.00, 'PAID',    '2026-07-22 11:00:00'),
(20, 20,  900.00, 1300.00, 18.00,  396.00,  2596.00, 'PARTIAL', '2026-08-06 10:00:00');

-- ---------------------------------------------------------------------------
-- Payments  (full for PAID, partial for PARTIAL, none for PENDING)
-- ---------------------------------------------------------------------------
INSERT INTO payments (bill_id, amount, payment_method, payment_date, transaction_ref, recorded_by)
VALUES
(1,  4366.00, 'UPI',  '2026-01-10 11:05:00', 'UPI-JAN-001', 2),
(2,  2242.00, 'CARD', '2026-01-12 12:10:00', 'CRD-JAN-002', 2),
(3,  2832.00, 'CASH', '2026-01-15 10:40:00', NULL,          2),
(4,  1298.00, 'UPI',  '2026-01-18 11:40:00', 'UPI-JAN-004', 2),
(5,  1298.00, 'CARD', '2026-02-03 10:15:00', 'CRD-FEB-005', 2),
(6,  3304.00, 'UPI',  '2026-02-08 13:20:00', 'UPI-FEB-006', 2),
(7,  2419.00, 'CASH', '2026-02-14 10:20:00', NULL,          2),
(8,  2419.00, 'CARD', '2026-02-20 14:15:00', 'CRD-FEB-008', 2),
(9,  1180.00, 'UPI',  '2026-03-02 12:10:00', 'UPI-MAR-009', 2),
(10, 2242.00, 'CASH', '2026-03-11 11:20:00', NULL,          2),
(11, 1357.00, 'UPI',  '2026-03-22 15:10:00', 'UPI-MAR-011', 2),
(12, 3894.00, 'CARD', '2026-04-05 12:40:00', 'CRD-APR-012', 2),
(13, 2714.00, 'UPI',  '2026-04-16 09:45:00', 'UPI-APR-013', 2),
(14, 1500.00, 'CASH', '2026-05-07 13:40:00', NULL,          2),
(16, 2301.00, 'UPI',  '2026-06-04 11:15:00', 'UPI-JUN-016', 2),
(18, 2478.00, 'CARD', '2026-07-09 10:40:00', 'CRD-JUL-018', 2),
(19, 1121.00, 'UPI',  '2026-07-22 11:10:00', 'UPI-JUL-019', 2),
(20, 1000.00, 'CASH', '2026-08-06 10:15:00', NULL,          2);
