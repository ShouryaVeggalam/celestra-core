# DBMS Mini Project Report

## Hospital Patient & Appointment Management System

**Programme:** B.Tech (Computer Science and Engineering)  
**Semester:** III  
**Subject:** Database Management Systems  
**Academic Year:** 2025–26  

---

# STEP 1: TITLE SELECTION

## 1.1 Project Title

**Hospital Patient & Appointment Management System**

## 1.2 Domain

Healthcare Information Systems / Hospital Management (Outpatient Operations)

## 1.3 Technology Stack

| Layer | Technology |
|---|---|
| Database Management System | MySQL 8.0+ (InnoDB storage engine) |
| Character Set | utf8mb4 / utf8mb4_unicode_ci |
| Database Language | SQL (DDL, DML, DQL, DCL, TCL) |
| Database Objects | Tables, Views, Stored Procedures, Triggers, Indexes |
| Integrity Mechanisms | Primary Key, Foreign Key, UNIQUE, CHECK, DEFAULT, ENUM |
| Transaction Model | ACID-compliant InnoDB transactions (BEGIN / COMMIT / ROLLBACK / SAVEPOINT) |
| Security | Role-based user accounts; hashed credentials; GRANT / REVOKE privileges |
| Front-end (optional for demonstration) | Web-based reception / doctor / admin interface |
| Back-end (optional for demonstration) | Application server connecting to `hospital_db` |

## 1.4 One-line Project Description

A relational database system that centrally stores and manages hospital patients, doctors, departments, appointments, treatments, bills, and payments, while enforcing data integrity, role-based access, and conflict-free outpatient scheduling.

---

# STEP 2: PROBLEM STATEMENT

Hospitals of small and medium scale in India still depend, in many departments, on paper registers, telephone bookings, and disconnected spreadsheets. Patient details are written in one register, appointment slots in another, clinical notes on loose case sheets, and billing in a separate cash-book. Because these records are not linked, reception cannot instantly verify whether a doctor is already booked, clinicians cannot retrieve a prior diagnosis without searching physical files, and accounts cannot determine outstanding dues without manual reconciliation. Duplicate patient entries, overlapping appointments, misplaced prescriptions, and delayed bill settlement are therefore common. Handwritten errors in blood-group or emergency-contact information further compromise urgent care.

The volume of outpatient traffic makes such processes unsustainable. If two receptionists book the same slot, the clash is discovered only when patients arrive. Goods and Services Tax (GST) inclusive billing calculated by hand is error-prone, and partial payments are difficult to track. Administration also lacks timely reports on department-wise load, pending revenue, and doctor availability. Confidentiality is weak: paper files can be read or misplaced, and there is no role-based restriction on who may alter a record.

An automated relational database is therefore required as the single source of truth for outpatient operations. The proposed Hospital Patient and Appointment Management System stores patients, doctors, departments, appointments, treatments, bills, payments, and authenticated users in a normalised MySQL schema. Its scope covers patient registration, doctor profiles against departments, conflict-free appointment booking, recording of diagnosis after a completed visit, GST-compliant billing, cash, card, or UPI payments including partial settlement, and operational reports. In-patient wards, pharmacy inventory, laboratory systems, and insurance claims are excluded. The system enforces referential integrity, unique contact identifiers, role-based login, and transactional consistency so that clinical and financial data remain accurate, secure, and queryable.

*(Word count: 290)*

---

# STEP 3: OBJECTIVES

The principal objectives of this mini-project are as follows:

**3.1 Patient Management**  
To design and implement a centralised patient registry that captures demographic, contact, blood-group, and emergency-contact details, prevents duplicate registrations through unique phone numbers, and supports rapid retrieval of a patient’s complete visit history.

**3.2 Doctor Management**  
To maintain structured doctor profiles linked to hospital departments, including specialisation, qualification, consultation fee, working hours, and availability status, and to associate each doctor with a unique authenticated user account.

**3.3 Department Organisation**  
To store hospital departments as an independent lookup entity so that department names and floor locations are recorded once and reused by all doctors, thereby avoiding redundant and inconsistent departmental data.

**3.4 Appointment Scheduling**  
To enable conflict-free outpatient appointment booking by validating doctor working hours, preventing double-booking of active slots, permitting reuse of cancelled slots, and recording appointment status as Scheduled, Completed, or Cancelled.

**3.5 Treatment Records**  
To record diagnosis, prescription, clinical notes, and treatment charges against each completed appointment on a one-to-one basis, so that every consultation has a single, authoritative clinical record.

**3.6 Billing and Payments**  
To generate GST-inclusive bills from consultation fees and treatment charges, to support full and partial payments through Cash, Card, or UPI, and to automatically update bill status as Pending, Partial, or Paid.

**3.7 Data Integrity**  
To enforce entity integrity (primary keys), referential integrity (foreign keys with appropriate ON UPDATE / ON DELETE actions), domain integrity (ENUM, CHECK, DEFAULT), and uniqueness constraints so that invalid, orphaned, or duplicate records cannot persist.

**3.8 Security and Access Control**  
To restrict system access through authenticated users with roles of Administrator, Doctor, and Receptionist; to store passwords only in hashed form; and to apply database privileges so that each role can perform only authorised operations.

**3.9 Report Generation**  
To provide reusable views and queries for patient history, doctor schedules, pending bills, department-wise load, monthly revenue, and outstanding dues, thereby supporting both operational reporting and management decision-making.

**3.10 Transactional Reliability**  
To execute critical operations such as appointment booking and payment recording inside ACID transactions, so that concurrent users cannot leave the database in a half-updated or inconsistent state.

---

# STEP 4: REQUIREMENTS GATHERING

Requirements were gathered by studying typical outpatient hospital workflows (registration → appointment → consultation → billing → payment) and by mapping those workflows onto DBMS constructs required for a third-semester mini-project.

## 4.1 Functional Requirements

| S. No. | ID | Functional Requirement |
|---|---|---|
| 1 | FR-01 | The system shall register a new patient with name, gender, date of birth, phone, address, blood group, and optional email and emergency contact. |
| 2 | FR-02 | The system shall uniquely identify every patient by `patient_id` and shall reject a second registration that uses the same phone number. |
| 3 | FR-03 | The system shall maintain department master data (name, description, floor) and shall not allow two departments with the same name. |
| 4 | FR-04 | The system shall register doctors against a department and a unique user account, capturing specialisation, qualification, phone, working hours, consultation fee, and availability. |
| 5 | FR-05 | The system shall book an appointment for a patient with a chosen doctor on a given date and time, recording the reason for visit. |
| 6 | FR-06 | The system shall reject an appointment that falls outside the doctor’s `available_from`–`available_to` window or that collides with an already Scheduled or Completed slot. |
| 7 | FR-07 | The system shall allow cancellation of an appointment and shall thereafter permit the same slot to be re-booked. |
| 8 | FR-08 | The system shall record exactly one treatment (diagnosis, prescription, notes, charges) for a completed appointment. |
| 9 | FR-09 | The system shall generate exactly one bill per appointment, comprising consultation fee, treatment charges, GST rate, GST amount, and total amount. |
| 10 | FR-10 | The system shall record one or more payments against a bill using Cash, Card, or UPI, including partial payments, and shall update bill status to Pending, Partial, or Paid. |
| 11 | FR-11 | The system shall authenticate users with unique usernames and emails, assign a role of Admin, Doctor, or Receptionist, and allow deactivation of an account without deleting historical records. |
| 12 | FR-12 | The system shall produce a complete patient history combining appointments, treating doctors, departments, diagnoses, prescriptions, and billing status. |
| 13 | FR-13 | The system shall produce a doctor schedule showing booked patients, times, and appointment status. |
| 14 | FR-14 | The system shall list pending and partially paid bills together with the outstanding amount. |
| 15 | FR-15 | The system shall write an append-only audit entry whenever a payment is inserted, for later financial review. |
| 16 | FR-16 | The system shall support operational queries such as today’s appointments, department-wise patient counts, monthly revenue, and top bills. |

## 4.2 Non-Functional Requirements

| S. No. | ID | Category | Non-Functional Requirement |
|---|---|---|---|
| 1 | NFR-01 | Performance | Patient-name search, doctor-wise appointment listing, and “today’s appointments” shall be supported by indexes so that typical operational queries complete within interactive time on a dataset of several thousand rows. |
| 2 | NFR-02 | Scalability | The schema shall accommodate additional departments, doctors, patients, and years of historical appointments without structural redesign; surrogate integer keys and InnoDB clustering support growth of transactional tables. |
| 3 | NFR-03 | Security | Passwords shall be stored only as hashes; application roles shall map to database privileges; doctors shall not freely alter billing data; deactivated users (`is_active = FALSE`) shall be denied login. |
| 4 | NFR-04 | Reliability | Critical booking and payment sequences shall execute inside transactions with exception handlers so that a mid-operation failure leaves no partial row set. |
| 5 | NFR-05 | Availability | The InnoDB engine and a dedicated `hospital_db` database shall remain independently restorable from backup; foreign-key checks shall be re-enabled after scripted rebuilds so the schema can be recreated cleanly for demonstration. |
| 6 | NFR-06 | Data Consistency | Primary keys, foreign keys, UNIQUE constraints, CHECK constraints, and triggers shall guarantee that bills, treatments, and appointments remain mutually consistent (for example, a treatment cannot exist without its appointment). |
| 7 | NFR-07 | Maintainability | Schema objects shall be organised into numbered scripts (tables, seed data, queries, views, procedures, triggers, indexes, transactions) with named constraints to simplify viva demonstration and future alteration. |
| 8 | NFR-08 | Usability | Views such as `patient_history`, `doctor_schedule`, and `pending_bills` shall hide multi-table joins from end users and from the application layer, presenting a single readable result set per operational task. |
| 9 | NFR-09 | Integrity of Concurrent Access | Row-level locking (`FOR UPDATE`) shall be used while booking a slot or settling a bill so that two concurrent receptionists cannot double-book a doctor or over-pay the same bill. |
| 10 | NFR-10 | Auditability | Every payment insert shall produce a corresponding `payment_audit` row that is not overwritten, supporting later inspection of who recorded what amount and by which method. |

---

# STEP 5: ENTITY RELATIONSHIP (ER) MODELLING

The conceptual design identifies eight core entities corresponding to the outpatient workflow, plus one supporting audit entity.

## 5.1 Entity Catalogue

### 5.1.1 PATIENT

| Item | Description |
|---|---|
| **Purpose** | Stores demographic and contact information of every registered outpatient. |
| **Attributes** | `patient_id`, `first_name`, `last_name`, `gender`, `dob`, `phone`, `email`, `address`, `blood_group`, `emergency_contact`, `created_at` |
| **Primary Key** | `patient_id` |
| **Derived (not stored)** | Age is computed from `dob` at query time so that a stored age cannot become stale (3NF). |
| **Important Relationships** | One Patient **has many** Appointments. One Patient **has many** Bills. |

### 5.1.2 DOCTOR

| Item | Description |
|---|---|
| **Purpose** | Stores professional profile, working hours, and fee of each consulting doctor. |
| **Attributes** | `doctor_id`, `user_id`, `department_id`, `first_name`, `last_name`, `specialization`, `qualification`, `phone`, `available_from`, `available_to`, `consultation_fee`, `is_available`, `created_at` |
| **Primary Key** | `doctor_id` |
| **Important Relationships** | One Doctor **belongs to** one Department. One Doctor **is linked to** one User (1:1). One Doctor **has many** Appointments. |

### 5.1.3 DEPARTMENT

| Item | Description |
|---|---|
| **Purpose** | Independent lookup of hospital departments; avoids storing department name on every doctor row. |
| **Attributes** | `department_id`, `name`, `description`, `floor`, `created_at` |
| **Primary Key** | `department_id` |
| **Important Relationships** | One Department **has many** Doctors. |

### 5.1.4 APPOINTMENT

| Item | Description |
|---|---|
| **Purpose** | Represents a scheduled consultation between one patient and one doctor at a specific date and time. |
| **Attributes** | `appointment_id`, `patient_id`, `doctor_id`, `appointment_date`, `appointment_time`, `status`, `reason`, `created_at` |
| **Primary Key** | `appointment_id` |
| **Important Relationships** | Many Appointments **belong to** one Patient. Many Appointments **belong to** one Doctor. One Appointment **has at most one** Treatment. One Appointment **has at most one** Bill. |

### 5.1.5 TREATMENT

| Item | Description |
|---|---|
| **Purpose** | Clinical outcome of a completed appointment: diagnosis, prescription, notes, and charges. |
| **Attributes** | `treatment_id`, `appointment_id`, `diagnosis`, `prescription`, `treatment_notes`, `treatment_charges`, `created_at` |
| **Primary Key** | `treatment_id` |
| **Important Relationships** | One Treatment **belongs to** exactly one Appointment (1:1). Treatment charges flow into the related Bill. |

### 5.1.6 BILL

| Item | Description |
|---|---|
| **Purpose** | Financial document for a completed visit. Amounts are stored (not recomputed solely at read time) because the GST rate applicable on the day of generation must be preserved historically. |
| **Attributes** | `bill_id`, `patient_id`, `appointment_id`, `consultation_fee`, `treatment_charges`, `gst_rate`, `gst_amount`, `total_amount`, `status`, `generated_at` |
| **Primary Key** | `bill_id` |
| **Important Relationships** | One Bill **belongs to** one Patient. One Bill **belongs to** one Appointment (1:1). One Bill **has many** Payments. |

### 5.1.7 PAYMENT

| Item | Description |
|---|---|
| **Purpose** | A single receipt against a bill; several payments may settle one bill (partial payment model). |
| **Attributes** | `payment_id`, `bill_id`, `amount`, `payment_method`, `payment_date`, `transaction_ref`, `recorded_by` |
| **Primary Key** | `payment_id` |
| **Important Relationships** | Many Payments **belong to** one Bill. A Payment **may be recorded by** one User (receptionist / admin). Each Payment insert **produces** one Payment_Audit row. |

### 5.1.8 USER

| Item | Description |
|---|---|
| **Purpose** | Authentication and authorisation for Admin, Doctor, and Receptionist staff. |
| **Attributes** | `user_id`, `username`, `email`, `password_hash`, `role`, `is_active`, `created_at` |
| **Primary Key** | `user_id` |
| **Important Relationships** | One User **may correspond to** one Doctor (1:1 for doctor accounts). One User **may record** many Payments. |

### 5.1.9 Supporting Entity: PAYMENT_AUDIT (not a core business entity)

An append-only log written by a trigger whenever a payment is inserted. Controlled redundancy is intentional; the table is not required to satisfy 3NF because it is an audit trail rather than a normalised business fact.

| Item | Description |
|---|---|
| **Attributes** | `audit_id`, `payment_id`, `bill_id`, `amount`, `payment_method`, `action`, `created_at` |
| **Primary Key** | `audit_id` |

## 5.2 Relationship Summary

| Relationship | Cardinality | Description |
|---|---|---|
| DEPARTMENT – DOCTOR | 1 : N | Each doctor belongs to exactly one department; a department employs many doctors. |
| USER – DOCTOR | 1 : 1 | Each doctor account maps to exactly one user; a doctor user is not shared. |
| PATIENT – APPOINTMENT | 1 : N | A patient may have many visits over time. |
| DOCTOR – APPOINTMENT | 1 : N | A doctor may have many slots; an appointment has one doctor. |
| APPOINTMENT – TREATMENT | 1 : 1 | A completed appointment has at most one treatment record. |
| APPOINTMENT – BILL | 1 : 1 | A completed appointment has at most one bill. |
| PATIENT – BILL | 1 : N | A patient accumulates bills across visits. |
| BILL – PAYMENT | 1 : N | A bill may be settled in one or more instalments. |
| USER – PAYMENT | 1 : N | A receptionist or admin may record many payments. |
| PAYMENT – PAYMENT_AUDIT | 1 : 1 (log) | Every insert is mirrored into the audit log. |

## 5.3 Complete Mermaid ER Diagram

```mermaid
erDiagram
    DEPARTMENT ||--o{ DOCTOR : "employs"
    USER ||--o| DOCTOR : "authenticates"
    USER ||--o{ PAYMENT : "records"
    PATIENT ||--o{ APPOINTMENT : "books"
    DOCTOR ||--o{ APPOINTMENT : "consults"
    PATIENT ||--o{ BILL : "is billed"
    APPOINTMENT ||--o| TREATMENT : "results in"
    APPOINTMENT ||--o| BILL : "generates"
    BILL ||--o{ PAYMENT : "is settled by"
    PAYMENT ||--o| PAYMENT_AUDIT : "is logged as"

    DEPARTMENT {
        int department_id PK
        varchar name UK
        varchar description
        varchar floor
        timestamp created_at
    }

    USER {
        int user_id PK
        varchar username UK
        varchar email UK
        varchar password_hash
        enum role
        boolean is_active
        timestamp created_at
    }

    DOCTOR {
        int doctor_id PK
        int user_id FK_UK
        int department_id FK
        varchar first_name
        varchar last_name
        varchar specialization
        varchar qualification
        varchar phone UK
        time available_from
        time available_to
        decimal consultation_fee
        boolean is_available
        timestamp created_at
    }

    PATIENT {
        int patient_id PK
        varchar first_name
        varchar last_name
        enum gender
        date dob
        varchar phone UK
        varchar email
        varchar address
        enum blood_group
        varchar emergency_contact
        timestamp created_at
    }

    APPOINTMENT {
        int appointment_id PK
        int patient_id FK
        int doctor_id FK
        date appointment_date
        time appointment_time
        enum status
        varchar reason
        timestamp created_at
    }

    TREATMENT {
        int treatment_id PK
        int appointment_id FK_UK
        varchar diagnosis
        text prescription
        text treatment_notes
        decimal treatment_charges
        timestamp created_at
    }

    BILL {
        int bill_id PK
        int patient_id FK
        int appointment_id FK_UK
        decimal consultation_fee
        decimal treatment_charges
        decimal gst_rate
        decimal gst_amount
        decimal total_amount
        enum status
        timestamp generated_at
    }

    PAYMENT {
        int payment_id PK
        int bill_id FK
        decimal amount
        enum payment_method
        timestamp payment_date
        varchar transaction_ref
        int recorded_by FK
    }

    PAYMENT_AUDIT {
        int audit_id PK
        int payment_id
        int bill_id
        decimal amount
        varchar payment_method
        varchar action
        timestamp created_at
    }
```

**Legend:** `PK` = Primary Key, `FK` = Foreign Key, `UK` = Unique Key, `FK_UK` = Foreign Key that is also Unique (implements 1:1).

---

# STEP 6: SCHEMA DESIGN (RELATIONAL MODEL)

The ER model is converted into relations (tables) under MySQL 8.0 InnoDB. Each table below lists attributes, data types, keys, and constraints as implemented in the project database `hospital_db`.

## 6.1 Mapping Rules Applied

1. Each entity becomes a table; each atomic attribute becomes a column.  
2. A 1:N relationship is implemented by placing the parent’s primary key as a foreign key on the child.  
3. A 1:1 relationship is implemented by a foreign key that is also UNIQUE (`doctors.user_id`, `treatments.appointment_id`, `bills.appointment_id`).  
4. Multi-valued or repeating groups are not used; payments are a separate table rather than repeating columns on `bills`.  
5. Lookup data (department name) is factored into its own table to remove transitive dependency.

## 6.2 Relational Schema

### 6.2.1 Table: `users`

| Attribute | Data Type | Null | Default | Constraints |
|---|---|---|---|---|
| user_id | INT | NOT NULL | AUTO_INCREMENT | **PRIMARY KEY** |
| username | VARCHAR(50) | NOT NULL | — | UNIQUE; CHECK (CHAR_LENGTH ≥ 3) |
| email | VARCHAR(100) | NOT NULL | — | UNIQUE |
| password_hash | VARCHAR(255) | NOT NULL | — | Stores hashed password only |
| role | ENUM('ADMIN','DOCTOR','RECEPTIONIST') | NOT NULL | — | Domain integrity |
| is_active | BOOLEAN | NOT NULL | TRUE | Soft disable |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | Audit stamp |

**Primary Key:** `user_id`  
**Foreign Keys:** None  
**Engine:** InnoDB  

---

### 6.2.2 Table: `departments`

| Attribute | Data Type | Null | Default | Constraints |
|---|---|---|---|---|
| department_id | INT | NOT NULL | AUTO_INCREMENT | **PRIMARY KEY** |
| name | VARCHAR(80) | NOT NULL | — | UNIQUE |
| description | VARCHAR(255) | NULL | — | — |
| floor | VARCHAR(20) | NOT NULL | `'1'` | — |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | — |

**Primary Key:** `department_id`  
**Foreign Keys:** None  

---

### 6.2.3 Table: `doctors`

| Attribute | Data Type | Null | Default | Constraints |
|---|---|---|---|---|
| doctor_id | INT | NOT NULL | AUTO_INCREMENT | **PRIMARY KEY** |
| user_id | INT | NOT NULL | — | UNIQUE; **FK → users(user_id)** ON UPDATE CASCADE ON DELETE RESTRICT |
| department_id | INT | NOT NULL | — | **FK → departments(department_id)** ON UPDATE CASCADE ON DELETE RESTRICT |
| first_name | VARCHAR(60) | NOT NULL | — | — |
| last_name | VARCHAR(60) | NOT NULL | — | — |
| specialization | VARCHAR(80) | NOT NULL | — | — |
| qualification | VARCHAR(80) | NOT NULL | — | — |
| phone | VARCHAR(15) | NOT NULL | — | UNIQUE |
| available_from | TIME | NOT NULL | `'09:00:00'` | CHECK (`available_to` > `available_from`) |
| available_to | TIME | NOT NULL | `'17:00:00'` | (paired with above CHECK) |
| consultation_fee | DECIMAL(10,2) | NOT NULL | 500.00 | CHECK (≥ 0) |
| is_available | BOOLEAN | NOT NULL | TRUE | — |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | — |

**Primary Key:** `doctor_id`  
**Foreign Keys:** `user_id`, `department_id`  

---

### 6.2.4 Table: `patients`

| Attribute | Data Type | Null | Default | Constraints |
|---|---|---|---|---|
| patient_id | INT | NOT NULL | AUTO_INCREMENT | **PRIMARY KEY** |
| first_name | VARCHAR(60) | NOT NULL | — | CHECK (CHAR_LENGTH ≥ 1) |
| last_name | VARCHAR(60) | NOT NULL | — | — |
| gender | ENUM('MALE','FEMALE','OTHER') | NOT NULL | — | Domain integrity |
| dob | DATE | NOT NULL | — | Age derived at query time |
| phone | VARCHAR(15) | NOT NULL | — | UNIQUE |
| email | VARCHAR(100) | NULL | — | — |
| address | VARCHAR(255) | NOT NULL | — | Atomic street-level string |
| blood_group | ENUM('A+','A-','B+','B-','AB+','AB-','O+','O-') | NOT NULL | — | Domain integrity |
| emergency_contact | VARCHAR(15) | NULL | — | — |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | — |

**Primary Key:** `patient_id`  
**Foreign Keys:** None  

---

### 6.2.5 Table: `appointments`

| Attribute | Data Type | Null | Default | Constraints |
|---|---|---|---|---|
| appointment_id | INT | NOT NULL | AUTO_INCREMENT | **PRIMARY KEY** |
| patient_id | INT | NOT NULL | — | **FK → patients(patient_id)** ON UPDATE CASCADE ON DELETE RESTRICT |
| doctor_id | INT | NOT NULL | — | **FK → doctors(doctor_id)** ON UPDATE CASCADE ON DELETE RESTRICT |
| appointment_date | DATE | NOT NULL | — | CHECK (≥ '2020-01-01') |
| appointment_time | TIME | NOT NULL | — | Combined with doctor and status in a trigger to block double-booking |
| status | ENUM('SCHEDULED','COMPLETED','CANCELLED') | NOT NULL | `'SCHEDULED'` | Domain integrity |
| reason | VARCHAR(255) | NOT NULL | `'General consultation'` | — |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | — |

**Primary Key:** `appointment_id`  
**Foreign Keys:** `patient_id`, `doctor_id`  

**Design note:** A UNIQUE index on (doctor, date, time) is intentionally omitted. Cancelled slots must be reusable; a UNIQUE index would forbid that. Duplicate *active* slots are rejected by a BEFORE INSERT trigger.

---

### 6.2.6 Table: `treatments`

| Attribute | Data Type | Null | Default | Constraints |
|---|---|---|---|---|
| treatment_id | INT | NOT NULL | AUTO_INCREMENT | **PRIMARY KEY** |
| appointment_id | INT | NOT NULL | — | UNIQUE; **FK → appointments(appointment_id)** ON UPDATE CASCADE ON DELETE CASCADE |
| diagnosis | VARCHAR(255) | NOT NULL | — | — |
| prescription | TEXT | NOT NULL | — | — |
| treatment_notes | TEXT | NULL | — | — |
| treatment_charges | DECIMAL(10,2) | NOT NULL | 0.00 | CHECK (≥ 0) |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | — |

**Primary Key:** `treatment_id`  
**Foreign Keys:** `appointment_id`  

---

### 6.2.7 Table: `bills`

| Attribute | Data Type | Null | Default | Constraints |
|---|---|---|---|---|
| bill_id | INT | NOT NULL | AUTO_INCREMENT | **PRIMARY KEY** |
| patient_id | INT | NOT NULL | — | **FK → patients(patient_id)** ON UPDATE CASCADE ON DELETE RESTRICT |
| appointment_id | INT | NOT NULL | — | UNIQUE; **FK → appointments(appointment_id)** ON UPDATE CASCADE ON DELETE RESTRICT |
| consultation_fee | DECIMAL(10,2) | NOT NULL | — | Snapshot of doctor fee at billing time |
| treatment_charges | DECIMAL(10,2) | NOT NULL | 0.00 | Kept in sync by trigger when treatment changes |
| gst_rate | DECIMAL(5,2) | NOT NULL | 18.00 | CHECK (0 ≤ gst_rate ≤ 28) |
| gst_amount | DECIMAL(10,2) | NOT NULL | — | Stored historically |
| total_amount | DECIMAL(10,2) | NOT NULL | — | CHECK (≥ 0) |
| status | ENUM('PENDING','PARTIAL','PAID') | NOT NULL | `'PENDING'` | Updated by payment trigger |
| generated_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | — |

**Primary Key:** `bill_id`  
**Foreign Keys:** `patient_id`, `appointment_id`  

**Design note:** `gst_amount` and `total_amount` are stored rather than computed only at read time, because the GST rate applicable on the generation date must remain historically correct even if the default rate later changes.

---

### 6.2.8 Table: `payments`

| Attribute | Data Type | Null | Default | Constraints |
|---|---|---|---|---|
| payment_id | INT | NOT NULL | AUTO_INCREMENT | **PRIMARY KEY** |
| bill_id | INT | NOT NULL | — | **FK → bills(bill_id)** ON UPDATE CASCADE ON DELETE RESTRICT |
| amount | DECIMAL(10,2) | NOT NULL | — | CHECK (> 0) |
| payment_method | ENUM('CASH','CARD','UPI') | NOT NULL | — | Domain integrity |
| payment_date | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | — |
| transaction_ref | VARCHAR(60) | NULL | — | Optional UPI / card reference |
| recorded_by | INT | NULL | — | **FK → users(user_id)** ON UPDATE CASCADE ON DELETE SET NULL |

**Primary Key:** `payment_id`  
**Foreign Keys:** `bill_id`, `recorded_by`  

---

### 6.2.9 Table: `payment_audit` (supporting log)

| Attribute | Data Type | Null | Default | Constraints |
|---|---|---|---|---|
| audit_id | INT | NOT NULL | AUTO_INCREMENT | **PRIMARY KEY** |
| payment_id | INT | NOT NULL | — | Copied from the payment row (no FK required for an append-only log) |
| bill_id | INT | NOT NULL | — | Copied for convenient reporting |
| amount | DECIMAL(10,2) | NOT NULL | — | Copied |
| payment_method | VARCHAR(10) | NOT NULL | — | Copied |
| action | VARCHAR(20) | NOT NULL | `'INSERT'` | — |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | — |

## 6.3 Referential Action Summary

| Child Table | Foreign Key | Parent | ON UPDATE | ON DELETE | Rationale |
|---|---|---|---|---|---|
| doctors | user_id | users | CASCADE | RESTRICT | A doctor login may be renamed; the doctor row must not vanish while appointments exist. |
| doctors | department_id | departments | CASCADE | RESTRICT | Department rename propagates; deletion is blocked if doctors remain. |
| appointments | patient_id | patients | CASCADE | RESTRICT | Visit history is preserved; a patient with appointments cannot be deleted. |
| appointments | doctor_id | doctors | CASCADE | RESTRICT | Same protection for doctor history. |
| treatments | appointment_id | appointments | CASCADE | CASCADE | Clinical notes belong only to that visit; removing the visit removes the treatment. |
| bills | patient_id | patients | CASCADE | RESTRICT | Financial history must not be silently erased. |
| bills | appointment_id | appointments | CASCADE | RESTRICT | A billed visit cannot be deleted without first handling the bill. |
| payments | bill_id | bills | CASCADE | RESTRICT | Receipts cannot outlive their bill in an uncontrolled way. |
| payments | recorded_by | users | CASCADE | SET NULL | If a staff account is removed, historical receipts remain with a null recorder. |

## 6.4 Normalisation (1NF, 2NF, 3NF)

The schema is designed to satisfy the first three normal forms required by the DBMS syllabus.

### 6.4.1 First Normal Form (1NF)

A relation is in 1NF if every attribute is atomic and there are no repeating groups.

**Evidence in this project:**

- Names are split into `first_name` and `last_name` rather than a single comma-separated string used as a list.  
- Multiple appointments of a patient are stored as separate rows in `appointments`, not as `appointment1`, `appointment2`, … columns.  
- Multiple payments against one bill are stored as separate rows in `payments`, not as repeating amount columns.  
- Blood group, gender, role, status, and payment method are single ENUM values, not sets.  
- Address is stored as one atomic descriptive string appropriate to the mini-project scope (further splitting into city/state/PIN is possible but not required for 1NF).

Hence every table is in **1NF**.

### 6.4.2 Second Normal Form (2NF)

A relation is in 2NF if it is in 1NF and every non-prime attribute is fully functionally dependent on the *whole* primary key (no partial dependency).

**Evidence in this project:**

- Every table uses a single-attribute surrogate primary key (`user_id`, `department_id`, `doctor_id`, `patient_id`, `appointment_id`, `treatment_id`, `bill_id`, `payment_id`, `audit_id`).  
- When the primary key is a single column, partial dependency on part of a composite key cannot occur.  
- Composite candidate keys (for example, doctor + date + time for an active slot) are enforced by a trigger rather than being used as the primary key, so non-key attributes such as `reason` and `status` depend on `appointment_id` alone.

Hence every table is in **2NF**.

### 6.4.3 Third Normal Form (3NF)

A relation is in 3NF if it is in 2NF and there is no transitive dependency of a non-prime attribute on the primary key through another non-prime attribute.

**Evidence in this project:**

| Potential violation if un-normalised | How 3NF is achieved |
|---|---|
| Storing `department_name` on `doctors` | Department name lives only in `departments`; `doctors` stores `department_id`. Doctor → department_id → name is a join, not a stored transitive fact. |
| Storing `age` on `patients` | Age is derived from `dob`; it is never stored, so it cannot disagree with the date of birth. |
| Storing `patient_name` on `appointments` or `bills` | Only `patient_id` is stored; the name is obtained by joining `patients`. |
| Storing `doctor_name` or `consultation_fee` as the only source of truth on `appointments` | Appointments store `doctor_id`. The fee snapshot is copied onto `bills` at generation time as a historical fact (the fee charged that day), not as a second master copy of the doctor’s current fee. |
| Repeating GST percentage as a computed-only field with no history | `gst_rate` is stored on each bill because it is a fact of that bill, not a transitive copy of a hospital-wide setting that may later change. |

Non-key attributes such as `specialization` describe the doctor, not the department; `diagnosis` describes the treatment, not the appointment slot; `payment_method` describes the payment, not the bill header. No non-prime attribute depends on another non-prime attribute.

Hence every *business* table is in **3NF**.

`payment_audit` is an intentional denormalised log (it copies amount and method already present in `payments`) and is excluded from the 3NF claim for the operational schema.

### 6.4.4 Summary of Normalisation

| Normal Form | Satisfied? | Brief Justification |
|---|---|---|
| 1NF | Yes | Atomic attributes; no repeating groups; one fact per cell. |
| 2NF | Yes | All primary keys are single attributes; no partial dependence. |
| 3NF | Yes | Lookup data and names live in their owner tables; derived age is not stored; historical bill amounts are facts of the bill, not transitive copies of master data. |

---

# STEP 7: SQL IMPLEMENTATION (DOCUMENTATION ONLY)

This section describes how Structured Query Language is used in the project. **No SQL statements are reproduced here**; the actual scripts reside in the project’s database folder and will be demonstrated separately during implementation and viva.

The database created for the project is named **`hospital_db`**. Implementation is organised into five language categories prescribed by the DBMS syllabus, plus supporting objects (views, procedures, triggers, and indexes) that are composed from those categories.

## 7.1 Data Definition Language (DDL)

**Purpose in this project.**  
DDL is used to create the database and to define the structure of all relations, including data types, primary keys, foreign keys, unique keys, check constraints, default values, and the InnoDB engine. DDL is also used to create views, stored procedures, triggers, and indexes after the base tables exist.

**What DDL accomplishes here:**

1. Creates the schema `hospital_db` with Unicode character support.  
2. Creates the nine tables listed in Section 7.6 in parent-to-child order.  
3. Attaches named constraints (`pk_*`, `fk_*`, `uq_*`, `chk_*`) so that integrity rules are explicit and easy to discuss in the viva.  
4. Creates three views that hide join complexity from the application (`patient_history`, `doctor_schedule`, `pending_bills`).  
5. Creates three stored procedures that encapsulate business rules (`BookAppointment`, `GenerateBill`, `GetPatientHistory`).  
6. Creates triggers that prevent double-booking, keep bill totals aligned with treatment charges, and write payment audit rows.  
7. Creates indexes on patient names, appointment dates, doctor-wise slots, and bill status to meet the performance requirement (NFR-01).

DDL is executed once (or re-executed during a clean rebuild) and does not insert business data.

## 7.2 Data Manipulation Language (DML)

**Purpose in this project.**  
DML is used to insert, update, and delete rows that represent real hospital events: a new patient, a booked slot, a completed visit, a generated bill, or a received payment.

**What DML accomplishes here:**

1. **INSERT** — seed and live data for users, departments, doctors, patients, appointments, treatments, bills, and payments.  
2. **UPDATE** — change of appointment status (Scheduled → Completed / Cancelled), revision of treatment charges (which a trigger then pushes onto the related bill), and automatic revision of bill status (Pending → Partial → Paid) after a payment.  
3. **DELETE** — restricted in production by foreign keys; used mainly during controlled rebuild of the demonstration database. Patient or doctor rows that still have appointments cannot be deleted (ON DELETE RESTRICT).

DML for booking and billing is wrapped in transactions (see TCL) so that a failed validation does not leave a half-written appointment or bill.

## 7.3 Data Query Language (DQL)

**Purpose in this project.**  
DQL (principally the SELECT statement and its clauses) is used to retrieve information for reception, clinicians, accounts, and management without altering stored data.

**What DQL accomplishes here:**

The project demonstrates the full query syllabus on hospital data, including:

| Syllabus construct | Hospital use |
|---|---|
| SELECT / WHERE | List female O+ patients; list today’s appointments. |
| ORDER BY | Rank doctors by consultation fee; list bills by amount. |
| GROUP BY / HAVING | Count patients per blood group; list departments with more than one doctor. |
| INNER JOIN | Appointment list with patient and doctor names. |
| LEFT JOIN | Doctors with zero appointments; patients who have never been billed. |
| SELF JOIN | Pairs of doctors who share a department. |
| Subquery (scalar, IN, EXISTS, correlated) | Doctors above average fee; patients who visited Cardiology; bills versus monthly average. |
| Aggregates (COUNT, SUM, AVG, MIN, MAX) | Revenue totals; fee statistics; department-wise unique patients. |
| CASE | Classify appointments as Upcoming / Closed / Dropped. |
| UNION | Combined contact directory of doctors and patients. |
| Views | Patient history, doctor schedule, pending bills with outstanding amount. |
| Stored-procedure SELECT | `GetPatientHistory` returns the history view for one patient. |

DQL is the reporting layer of the system and fulfils Objective 3.9.

## 7.4 Data Control Language (DCL)

**Purpose in this project.**  
DCL is used to grant and revoke privileges so that database users correspond to hospital roles and cannot exceed their duties.

**What DCL accomplishes here:**

| Role | Intended privileges (conceptual) |
|---|---|
| **Administrator** | Full rights on `hospital_db` (create users, manage departments and doctors, read all reports). |
| **Receptionist** | SELECT / INSERT / UPDATE on patients, appointments, bills, and payments; SELECT on doctors and departments; EXECUTE on `BookAppointment` and `GenerateBill`. No right to drop tables or alter schema. |
| **Doctor** | SELECT on own schedule and on treatments of assigned patients; INSERT / UPDATE on treatments for completed appointments; no UPDATE on payments or user passwords of others. |

Passwords are never stored in plain text (`password_hash` only). Accounts can be disabled with `is_active` without deleting rows, which preserves foreign-key history. REVOKE is used conceptually to withdraw a privilege when a staff member changes role or leaves the hospital.

DCL therefore implements Objective 3.8 (security) and NFR-03.

## 7.5 Transaction Control Language (TCL)

**Purpose in this project.**  
TCL is used to group related DML statements into atomic units that either all succeed or all fail, thereby demonstrating the ACID properties on hospital workflows.

**What TCL accomplishes here:**

| TCL command | Use in this project |
|---|---|
| START TRANSACTION / BEGIN | Opens a unit of work for booking an appointment or recording a payment. |
| COMMIT | Makes a validated booking or a successful payment durable. |
| ROLLBACK | Aborts a booking when the doctor is unavailable, the slot clashes, or a database error occurs; aborts a payment if the operation is cancelled (for example, card machine timeout). |
| SAVEPOINT / ROLLBACK TO SAVEPOINT | Demonstrates partial undo within a larger transaction during the ACID viva script. |
| Row lock (FOR UPDATE) used inside the transaction | Prevents two receptionists from booking the same slot or over-paying the same bill concurrently. |

**ACID mapping:**

| Property | Demonstration |
|---|---|
| **Atomicity** | If the payment insert fails, bill status is not left half-updated. |
| **Consistency** | Foreign keys, CHECK constraints, and triggers still hold after COMMIT; a payment cannot reference a missing bill; amount must be greater than zero. |
| **Isolation** | Uncommitted work is invisible to other sessions; `FOR UPDATE` serialises cashiers on the same bill. |
| **Durability** | After COMMIT, InnoDB has persisted the change; a crash does not lose a recorded payment. |

TCL therefore implements Objective 3.10 and NFR-04 / NFR-09.

## 7.6 Tables Created

The following tables are created in `hospital_db`. Drop order on rebuild is child-to-parent so that foreign-key checks never fail.

| S. No. | Table | Role in the system | Approx. seed rows |
|---|---|---|---|
| 1 | `users` | Login identities for Admin, Receptionist, and Doctors | 10 |
| 2 | `departments` | Master list of clinical departments | 5 |
| 3 | `doctors` | Consulting staff linked to users and departments | 8 |
| 4 | `patients` | Outpatient registry | 20 |
| 5 | `appointments` | Booked, completed, and cancelled visits | 30 |
| 6 | `treatments` | Diagnosis and prescription for completed visits | 20 |
| 7 | `bills` | GST-inclusive invoices, one per completed appointment | 20 |
| 8 | `payments` | Receipts against bills (full and partial) | 18 |
| 9 | `payment_audit` | Trigger-written log of payment inserts | Grows with payments |

Supporting objects created after the tables:

| Object type | Names |
|---|---|
| Views | `patient_history`, `doctor_schedule`, `pending_bills` |
| Procedures | `BookAppointment`, `GenerateBill`, `GetPatientHistory` |
| Triggers | Prevent duplicate active appointments; refresh bill after treatment insert/update; audit payment and refresh bill status |
| Indexes | Patient first/last/full name; appointments by doctor, date, and slot; bills by status and patient |

## 7.7 Description of Sample Data

Sample data is inserted to make every relationship, constraint, and report demonstrable during the viva. It is realistic in structure but fictitious in identity.

### 7.7.1 Users (10 rows)

- One **Administrator** account for schema and master-data management.  
- One **Receptionist** account used as `recorded_by` on payments.  
- Eight **Doctor** accounts, each mapped 1:1 to a row in `doctors`.  
- Credentials are stored only as hashes. Roles cover all three ENUM values.

### 7.7.2 Departments (5 rows)

Cardiology, Neurology, Orthopedics, Pediatrics, and General Medicine, placed on floors 1–4. Two departments contain more than one doctor so that GROUP BY … HAVING and the doctor self-join have visible results.

### 7.7.3 Doctors (8 rows)

Eight specialists with distinct phones, qualifications (DM / MS / MD), working-hour windows, and consultation fees ranging from ₹500 to ₹1,200. Cardiology and Orthopedics each have two doctors; this supports department-wise reports and the “same department” self-join.

### 7.7.4 Patients (20 rows)

Twenty outpatients of mixed gender, age (including paediatric cases such as a 2016-born child), blood group, and city of residence. Unique phone numbers demonstrate the UNIQUE constraint. Names beginning with different letters support LIKE-based search. Female O+ patients exist so that a WHERE-clause filter returns a non-empty set.

### 7.7.5 Appointments (30 rows)

- **20 COMPLETED** visits (January–August 2026), each later given a treatment and a bill.  
- **2 CANCELLED** visits, demonstrating that a cancelled slot may be reused.  
- **8 SCHEDULED** future visits (September 2026), demonstrating the reception diary and the doctor-schedule view.  
- Reasons range from chest pain and migraine to vaccination review, giving meaningful diagnosis history.

### 7.7.6 Treatments (20 rows)

One treatment per completed appointment (1:1). Diagnoses include angina, osteoarthritis, Type 2 diabetes, focal epilepsy, and paediatric well-child visits. Treatment charges range from ₹250 to ₹2,500 so that GST and totals vary.

### 7.7.7 Bills (20 rows)

Each completed appointment has one bill. GST is applied at 18% on (consultation fee + treatment charges). Status mix is intentional:

- **PAID** — majority of bills, fully settled.  
- **PARTIAL** — two bills (for example, a ₹1,500 cash receipt against a larger total).  
- **PENDING** — two bills with no payment yet, so the `pending_bills` view is non-empty.

Storing `gst_rate`, `gst_amount`, and `total_amount` on each row preserves the historical invoice even if the hospital later changes its default GST rate.

### 7.7.8 Payments (18 rows)

Payments use all three methods (Cash, Card, UPI). Cash rows may have a null `transaction_ref`; electronic rows carry a reference code. All seed payments are recorded by the receptionist user. Two bills remain without a payment (Pending), and two bills have a payment smaller than the total (Partial), demonstrating the 1:N bill–payment model and the status trigger.

### 7.7.9 Payment audit

Audit rows are not hand-inserted. They are produced automatically when payments are inserted, demonstrating that DML on `payments` causes a trigger-written log without application code.

## 7.8 Implementation Script Map (for the report annexure)

| Script (conceptual) | Language category | Content |
|---|---|---|
| Create-tables script | DDL | Database, nine tables, PK / FK / UNIQUE / CHECK / DEFAULT |
| Dummy-data script | DML | Seed users, departments, doctors, patients, appointments, treatments, bills, payments |
| Queries script | DQL | Twenty-five SELECT demonstrations covering the syllabus |
| Views script | DDL (view definitions) + DQL (when queried) | Three operational views |
| Procedures script | DDL (procedure definitions); DML + TCL when executed | Booking, billing, patient history |
| Triggers script | DDL (trigger definitions); DML when fired | Double-book prevention, bill refresh, payment audit |
| Indexes script | DDL | Performance indexes |
| Transactions script | TCL (+ DML) | COMMIT, ROLLBACK, SAVEPOINT, ACID commentary |

---

# END OF STEPS 1–7

*This document contains only the analysis and design documentation for Steps 1 through 7. SQL source statements are intentionally omitted and will appear in the implementation annexure of the full project report.*
