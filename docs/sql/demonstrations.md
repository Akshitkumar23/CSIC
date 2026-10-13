# CSIC Relational SQL Learning & Demonstration Guide

This guide provides clear, practical examples of **Basic-to-Intermediate Relational SQL** using the PostgreSQL database designed for the **Cloud-Based Student Information Chatbot (CSIC)**.

All queries run directly against the 21 normalized 3NF tables in [`database/migrations/001_initial_schema.sql`](file:///d:/Projects/CSIC/database/migrations/001_initial_schema.sql) and the synthetic seed dataset in [`database/migrations/003_seed_data.sql`](file:///d:/Projects/CSIC/database/migrations/003_seed_data.sql).

---

## 1. Table of Contents
1. [Basic Queries: Filtering, Sorting & Limiting (`WHERE`, `ORDER BY`, `LIMIT`)](#1-basic-queries)
2. [Multi-Table Joins: `INNER JOIN` vs `LEFT JOIN`](#2-multi-table-joins)
3. [Aggregate Functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`)](#3-aggregate-functions)
4. [Grouping and Filtering Groups (`GROUP BY` and `HAVING`)](#4-group-by-and-having)
5. [Conditional Logic with `CASE` Expressions](#5-conditional-logic-with-case)
6. [Reusable Database Views (`CREATE VIEW`)](#6-reusable-database-views)
7. [Subqueries: Simple and Correlated](#7-subqueries)
8. [Database Integrity: Constraints and Basic Indexes](#8-database-integrity-and-indexes)
9. [Transaction Safety (ACID: `BEGIN`, `COMMIT`, `ROLLBACK`)](#9-database-transactions)
10. [Query Plan Inspection (`EXPLAIN`)](#10-query-plan-inspection)

---

## 1. Basic Queries

### 1.1 Filtering Active Students by Department
Retrieves all active students enrolled in the Computer Science department, ordered alphabetically.

```sql
SELECT 
    p.full_name,
    p.email,
    e.roll_number,
    e.status
FROM profiles p
JOIN enrollments e ON e.student_id = p.id
WHERE p.role = 'student' 
  AND e.status = 'active'
ORDER BY p.full_name ASC
LIMIT 10;
```

**Concept Explained:**
- `WHERE` filters rows before any grouping or projection.
- `ORDER BY ... ASC` sorts strings alphabetically.
- `LIMIT 10` limits the result size to prevent fetching excessive data across the network.

---

## 2. Multi-Table Joins

### 2.1 `INNER JOIN`: Student Course Schedule
An `INNER JOIN` returns rows only when there is a match in **both** tables. Here, it links students to their enrolled course, degree program, and semester.

```sql
SELECT 
    p.full_name AS student_name,
    e.roll_number,
    prog.code AS program,
    sem.semester_number,
    c.section
FROM enrollments e
INNER JOIN profiles p ON e.student_id = p.id
INNER JOIN courses c ON e.course_id = c.id
INNER JOIN programs prog ON c.program_id = prog.id
INNER JOIN semesters sem ON c.semester_id = sem.id
ORDER BY e.roll_number;
```

### 2.2 `LEFT JOIN`: Preserving Class Sessions with Zero Absences
A `LEFT JOIN` returns **all** records from the left table, and matched records from the right table (or `NULL` if no match exists). This ensures class sessions are not dropped if an attendance record has not yet been marked.

```sql
SELECT 
    cs.session_date,
    cs.topic,
    s.code AS subject_code,
    ar.status AS attendance_status,
    ar.remarks
FROM class_sessions cs
INNER JOIN faculty_assignments fa ON cs.faculty_assignment_id = fa.id
INNER JOIN subjects s ON fa.subject_id = s.id
LEFT JOIN attendance_records ar ON ar.session_id = cs.id
WHERE cs.status = 'conducted'
ORDER BY cs.session_date DESC
LIMIT 20;
```

---

## 3. Aggregate Functions

PostgreSQL provides five standard aggregate functions: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.

### 3.1 Examination Score Statistics
Calculates statistical metrics for an examination across all evaluated students.

```sql
SELECT 
    ex.name AS exam_name,
    ex.max_marks,
    COUNT(m.id) AS total_candidates,
    COUNT(CASE WHEN m.is_absent = FALSE THEN 1 END) AS candidates_appeared,
    ROUND(AVG(m.marks_obtained), 2) AS average_score,
    MIN(m.marks_obtained) AS lowest_score,
    MAX(m.marks_obtained) AS highest_score
FROM examinations ex
JOIN marks m ON m.examination_id = ex.id
WHERE ex.id = 'exam-001'
GROUP BY ex.name, ex.max_marks;
```

---

## 4. `GROUP BY` and `HAVING`

### 4.1 Grouping Rows by Subject
`GROUP BY` collapses rows with the same values into summary rows.

```sql
SELECT 
    s.code AS subject_code,
    s.name AS subject_name,
    COUNT(cs.id) AS conducted_sessions
FROM subjects s
JOIN faculty_assignments fa ON fa.subject_id = s.id
JOIN class_sessions cs ON cs.faculty_assignment_id = fa.id
WHERE cs.status = 'conducted'
GROUP BY s.code, s.name
ORDER BY s.code;
```

### 4.2 Filtering Aggregated Groups with `HAVING`
The `WHERE` clause filters individual rows **before** aggregation. The `HAVING` clause filters summary groups **after** aggregation.

```sql
-- Find subjects that have conducted at least 5 sessions
SELECT 
    s.code AS subject_code,
    s.name AS subject_name,
    COUNT(cs.id) AS conducted_sessions
FROM subjects s
JOIN faculty_assignments fa ON fa.subject_id = s.id
JOIN class_sessions cs ON cs.faculty_assignment_id = fa.id
WHERE cs.status = 'conducted'
GROUP BY s.code, s.name
HAVING COUNT(cs.id) >= 5
ORDER BY conducted_sessions DESC;
```

---

## 5. Conditional Logic with `CASE`

The `CASE` expression provides `if-then-else` conditional evaluation directly inside SQL queries.

### 5.1 Categorizing Student Attendance Standing
Classifies student attendance into clear academic warning categories:

```sql
SELECT 
    p.full_name AS student_name,
    e.roll_number,
    s.code AS subject_code,
    COUNT(CASE WHEN ar.status IN ('present', 'excused') THEN 1 END) AS attended_classes,
    COUNT(cs.id) AS total_classes,
    ROUND(
        (COUNT(CASE WHEN ar.status IN ('present', 'excused') THEN 1.0 END) * 100.0) 
        / NULLIF(COUNT(cs.id), 0), 
        2
    ) AS attendance_percentage,
    CASE 
        WHEN (COUNT(CASE WHEN ar.status IN ('present', 'excused') THEN 1.0 END) * 100.0) / NULLIF(COUNT(cs.id), 0) >= 75.00 
            THEN 'Eligible (Good Standing)'
        WHEN (COUNT(CASE WHEN ar.status IN ('present', 'excused') THEN 1.0 END) * 100.0) / NULLIF(COUNT(cs.id), 0) >= 65.00 
            THEN 'Warning: Medical Condonation Required'
        ELSE 'Critical: Detention Risk (< 65%)'
    END AS eligibility_status
FROM enrollments e
JOIN profiles p ON e.student_id = p.id
JOIN faculty_assignments fa ON fa.course_id = e.course_id
JOIN subjects s ON fa.subject_id = s.id
JOIN class_sessions cs ON cs.faculty_assignment_id = fa.id AND cs.status = 'conducted'
LEFT JOIN attendance_records ar ON ar.session_id = cs.id AND ar.enrollment_id = e.id
GROUP BY p.full_name, e.roll_number, s.code;
```

---

## 6. Reusable Database Views

A **View** is a saved query that can be queried like a table. Views simplify complex joins for application endpoints.

### 6.1 Attendance Overview View (`v_student_attendance`)
```sql
CREATE OR REPLACE VIEW v_student_attendance AS
SELECT 
    e.id AS enrollment_id,
    e.student_id,
    p.full_name AS student_name,
    e.roll_number,
    s.code AS subject_code,
    s.name AS subject_name,
    COUNT(cs.id) AS total_sessions_conducted,
    COUNT(CASE WHEN ar.status IN ('present', 'excused') THEN 1 END) AS attended_effective,
    COALESCE(
        ROUND(
            (COUNT(CASE WHEN ar.status IN ('present', 'excused') THEN 1.0 END) * 100.0) 
            / NULLIF(COUNT(cs.id), 0), 
            2
        ), 
        0.00
    ) AS attendance_percentage
FROM enrollments e
JOIN profiles p ON e.student_id = p.id
JOIN courses c ON e.course_id = c.id
JOIN faculty_assignments fa ON fa.course_id = c.id
JOIN subjects s ON fa.subject_id = s.id
LEFT JOIN class_sessions cs ON cs.faculty_assignment_id = fa.id AND cs.status = 'conducted'
LEFT JOIN attendance_records ar ON ar.session_id = cs.id AND ar.enrollment_id = e.id
GROUP BY e.id, e.student_id, p.full_name, e.roll_number, s.code, s.name;
```

---

## 7. Subqueries

### 7.1 Correlated Subquery for Invoice Payments
A subquery inside a `SELECT` statement computes total payments made against an enrollment without duplicating invoice rows:

```sql
SELECT 
    e.roll_number,
    p.full_name,
    fi.invoice_number,
    fi.amount AS invoice_amount,
    COALESCE(
        (SELECT SUM(fp.amount_paid) 
         FROM fee_payments fp 
         WHERE fp.invoice_id = fi.id AND fp.status = 'success'),
        0.00
    ) AS amount_paid
FROM fee_invoices fi
JOIN enrollments e ON fi.enrollment_id = e.id
JOIN profiles p ON e.student_id = p.id
WHERE fi.status != 'cancelled';
```

---

## 8. Database Integrity and Indexes

### 8.1 Constraints Enforcing Data Integrity
- `PRIMARY KEY (id)`: Ensures unique identity.
- `FOREIGN KEY (student_id) REFERENCES profiles(id) ON DELETE RESTRICT`: Prevents deleting a student profile while active enrollments exist.
- `CHECK (attendance_percentage BETWEEN 0 AND 100)`: Restricts numeric range.
- `UNIQUE (session_id, enrollment_id)`: Prevents duplicate attendance marking for the same student in the same class session.

### 8.2 Indexes Justified by Query Patterns
- `idx_attendance_session_enrollment` on `attendance_records(session_id, enrollment_id)`: Speeds up session attendance lookup.
- `idx_marks_exam_enrollment` on `marks(examination_id, enrollment_id)`: Speeds up report card generation.

---

## 9. Database Transactions

Transactions guarantee that multiple operations either **all succeed** or **all roll back** (Atomic, Consistent, Isolated, Durable).

```sql
-- Fee Payment Transaction Example
BEGIN;

-- 1. Insert payment record
INSERT INTO fee_payments (id, transaction_reference, invoice_id, amount_paid, payment_method, status)
VALUES (gen_random_uuid(), 'TXN-987654', 'inv-001', 25000.00, 'upi', 'success');

-- 2. Update invoice status to paid
UPDATE fee_invoices
SET status = 'paid', updated_at = NOW()
WHERE id = 'inv-001';

COMMIT;
```

---

## 10. Query Plan Inspection (`EXPLAIN`)

Use `EXPLAIN` to view how PostgreSQL executes a query without executing it:

```sql
EXPLAIN SELECT * FROM v_student_attendance WHERE student_id = 'stu-001';
```

- **Index Scan:** The database uses an index to locate rows directly (fast).
- **Sequential Scan (Seq Scan):** The database reads all rows in a table (expected on small lookup tables).
