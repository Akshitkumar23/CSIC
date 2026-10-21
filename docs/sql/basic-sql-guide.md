# CSIC — Basic-to-Intermediate Relational SQL Guide

**Author:** CSIC Engineering Team  
**Level:** Undergraduate / Final-Year B.Tech CSE  
**Target Database:** PostgreSQL 16+ / SQLite 3+  

---

## 1. Overview of the Relational Database Design

The **Cloud-Based Student Information Chatbot (CSIC)** uses a clean, normalized relational database consisting of **14 core tables**. Every feature in the student portal, admin dashboard, and AI chatbot executes genuine, parameterized ANSI SQL queries against these tables.

### The 14 Core Tables:
1. `users`: Master identity table with bcrypt-hashed passwords and roles (`student`, `faculty`, `admin`).
2. `courses`: Academic degree programs (e.g., `BTECH-CSE`).
3. `subjects`: Individual academic subjects mapped to semesters and faculty members.
4. `enrollments`: Student registrations linking a `user` to a `course` with unique `roll_number`.
5. `attendance_records`: Granular class-by-class attendance logs (`present`, `absent`, `excused`).
6. `examinations`: Scheduled assessment components with `max_marks` and dates.
7. `marks`: Scores achieved by enrolled students in examinations.
8. `fee_records`: Tuition invoice ledger tracking `amount`, `amount_paid`, and `status`.
9. `timetable_entries`: Weekly lecture time-slots mapped to subjects and lecture halls.
10. `notices`: University announcements categorized by priority and audience role.
11. `chat_history`: Audit trail storing student inquiries and verified chatbot replies.
12. `chat_sessions`: Conversational session tracking for multi-turn dialogues.
13. `chat_messages`: Granular student prompts and chatbot assistant responses per session.
14. `search_information`: Academic knowledge base for syllabus, timetables, fee FAQs, regulations, and marks schemes.

---

## 2. Core SQL Concepts Demonstrated in CSIC

This guide walks through 11 essential SQL queries implemented in the application code. Each example includes:
- **Application Feature**: Where and why this query is executed.
- **SQL Code**: Runnable parameterized query.
- **Clause Breakdown**: How each keyword works.
- **Viva Defense Tip**: How to clearly explain the query to evaluators during project defense.

---

### Example 1: Single-Table Filtering & Projection
**Application Feature:** Admin dashboard listing all registered students in alphabetical order.  
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `list_students()`

```sql
SELECT id, name, email, phone, created_at
FROM users
WHERE role = 'student' AND is_active = TRUE
ORDER BY name ASC;
```

#### Clause Breakdown:
- `SELECT id, name, email...`: **Projection** — returns only the necessary columns rather than using expensive `SELECT *`.
- `FROM users`: Specifies the base table.
- `WHERE role = 'student' AND is_active = TRUE`: **Selection / Filter** — filters rows using boolean predicate logic. Uses the index on `role` and `email`.
- `ORDER BY name ASC`: Sorts the returned rows alphabetically from A to Z.

> **💡 Viva Defense Tip:**  
> *"Explain why we avoid `SELECT *`: In production and cloud databases, `SELECT *` incurs unnecessary network bandwidth and memory overhead. Explicit column projection ensures schema changes don't break downstream serializers and enables index-only scan optimizations."*

---

### Example 2: Two-Table INNER JOIN
**Application Feature:** Student Profile lookup mapping user credentials to academic enrollment and roll number.  
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `get_student_detail()`

```sql
SELECT 
    u.id AS student_id,
    u.name AS full_name,
    u.email,
    e.roll_number,
    e.semester,
    e.section,
    c.name AS course_name
FROM users u
LEFT JOIN enrollments e ON e.user_id = u.id
LEFT JOIN courses c ON c.id = e.course_id
WHERE u.id = ? AND u.role = 'student';
```

#### Clause Breakdown:
- `LEFT JOIN enrollments e ON e.user_id = u.id`: Pairs each student account with their academic enrollment record where foreign key `e.user_id` matches primary key `u.id`. Using a `LEFT JOIN` guarantees newly onboarded students whose registration is pending still return their basic profile.
- `LEFT JOIN courses c ON c.id = e.course_id`: Traverses the second foreign key to fetch the descriptive program title.
- `WHERE u.id = ? AND u.role = 'student'`: Parameterized placeholder protecting against SQL injection while enforcing strict role authorization.

> **💡 Viva Defense Tip:**  
> *"Why prefer LEFT JOIN over INNER JOIN here? If an admitted student hasn't completed course section assignment yet, an INNER JOIN would return zero rows and cause an unexpected 404 profile error. A LEFT JOIN gracefully returns the student profile with NULL for unassigned course fields."*

---

### Example 3: Multi-Table JOIN for Report Card
**Application Feature:** Student marks breakdown and exam score display.  
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `get_student_marks_summary()`

```sql
SELECT 
    s.code AS subject_code,
    s.name AS subject_name,
    ex.name AS exam_name,
    m.marks_obtained,
    ex.max_marks,
    m.grade,
    ROUND((m.marks_obtained / ex.max_marks) * 100.0, 1) AS percentage
FROM enrollments e
INNER JOIN marks m ON m.enrollment_id = e.id
INNER JOIN examinations ex ON ex.id = m.examination_id
INNER JOIN subjects s ON s.id = ex.subject_id
WHERE e.user_id = ?
ORDER BY ex.exam_date ASC, s.code ASC;
```

#### Clause Breakdown:
- Traverses 4 normalized tables: `enrollments` -> `marks` -> `examinations` -> `subjects`.
- `ROUND((m.marks_obtained / ex.max_marks) * 100.0, 1)`: Computed column evaluating percentage dynamically in the database engine, rounded to 1 decimal place.

---

### Example 4: Conditional Aggregations with `CASE` and `GROUP BY`
**Application Feature:** Subject-by-subject attendance percentage calculation.  
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `get_student_attendance_summary()`

```sql
SELECT 
    s.code AS subject_code,
    s.name AS subject_name,
    COUNT(a.id) AS total_sessions,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS attended_sessions,
    SUM(CASE WHEN a.status = 'excused' THEN 1 ELSE 0 END) AS excused_sessions,
    SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS absent_sessions,
    ROUND(
        CAST(SUM(CASE WHEN a.status IN ('present', 'excused') THEN 1 ELSE 0 END) AS FLOAT) * 100.0 
        / NULLIF(COUNT(a.id), 0), 
        1
    ) AS attendance_percentage
FROM enrollments e
INNER JOIN subjects s ON s.course_id = e.course_id
LEFT JOIN attendance_records a ON a.enrollment_id = e.id AND a.subject_id = s.id
WHERE e.user_id = ?
GROUP BY s.id, s.code, s.name
ORDER BY s.code ASC;
```

#### Clause Breakdown:
- `LEFT JOIN attendance_records`: Ensures that even if a subject has zero attendance records yet, the subject still appears in the output with 0 classes.
- `CASE WHEN a.status = 'present' THEN 1 ELSE 0 END`: Evaluates each attendance log conditionally and transforms qualitative text into a binary digit (`1` or `0`) for mathematical summation.
- `NULLIF(COUNT(a.id), 0)`: **Defensive SQL design** — returns `NULL` if count is zero, preventing `ZeroDivisionError` crashes in the database.
- `GROUP BY s.id, s.code, s.name`: Collapses the multiple session rows into one summary row per subject.

> **💡 Viva Defense Tip:**  
> *"Why use `CASE` inside `SUM`? It avoids writing multiple queries with separate `WHERE status = 'present'` clauses. We scan the table once and aggregate present, excused, and absent counts in a single pass."*

---

### Example 5: Filtering Aggregated Groups with `HAVING`
**Application Feature:** Automated faculty alert identifying students with attendance below the mandatory 75% threshold.  
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `get_low_attendance_warnings()`

```sql
SELECT 
    u.id AS student_id,
    u.name AS student_name,
    e.roll_number,
    s.code AS subject_code,
    s.name AS subject_name,
    COUNT(a.id) AS total_sessions,
    SUM(CASE WHEN a.status IN ('present', 'excused') THEN 1 ELSE 0 END) AS attended_sessions,
    ROUND(
        CAST(SUM(CASE WHEN a.status IN ('present', 'excused') THEN 1 ELSE 0 END) AS FLOAT) * 100.0 
        / NULLIF(COUNT(a.id), 0), 
        1
    ) AS attendance_percentage
FROM enrollments e
INNER JOIN users u ON u.id = e.user_id
INNER JOIN subjects s ON s.course_id = e.course_id
INNER JOIN attendance_records a ON a.enrollment_id = e.id AND a.subject_id = s.id
GROUP BY u.id, u.name, e.roll_number, s.id, s.code, s.name
HAVING attendance_percentage < 75.0
ORDER BY attendance_percentage ASC;
```

#### Clause Breakdown:
- **`WHERE` vs. `HAVING`**: `WHERE` filters individual rows *before* aggregation; `HAVING` filters aggregated group results *after* `GROUP BY` calculation.
- Evaluates the computed percentage and filters out any student who has 75% or higher, returning strictly the roster of students at risk.

> **💡 Viva Defense Tip:**  
> *"A frequent interview question: 'Can you use aggregate functions in a WHERE clause?' No, because WHERE executes during row scan before groups exist. You must use HAVING to filter aggregated results."*

---

### Example 6: Arithmetic Balances & Financial Ledger
**Application Feature:** Student fee invoice summary and balance calculation.  
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `get_fee_summary()`

```sql
SELECT 
    f.id,
    f.invoice_number,
    f.title,
    f.amount,
    f.amount_paid,
    (f.amount - f.amount_paid) AS balance_due,
    f.due_date,
    f.status
FROM enrollments e
INNER JOIN fee_records f ON f.enrollment_id = e.id
WHERE e.user_id = ?
ORDER BY f.due_date ASC;
```

#### Clause Breakdown:
- `(f.amount - f.amount_paid) AS balance_due`: Computed expression showing exact outstanding fee liability.
- Demonstrates financial debit/credit balance tracking in a single clean table.

---

### Example 7: Daily Lecture Timetable Lookup
**Application Feature:** Chatbot schedule lookup ("What is my timetable today?").  
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `get_student_timetable()`

```sql
SELECT 
    t.day_of_week,
    t.start_time,
    t.end_time,
    t.room_number,
    s.code AS subject_code,
    s.name AS subject_name,
    COALESCE(u.name, 'Department Faculty') AS faculty_name
FROM enrollments e
INNER JOIN subjects s ON s.course_id = e.course_id
INNER JOIN timetable_entries t ON t.subject_id = s.id
LEFT JOIN users u ON u.id = s.faculty_id
WHERE e.user_id = ? AND t.day_of_week = ?
ORDER BY t.start_time ASC;
```

#### Clause Breakdown:
- `COALESCE(u.name, 'Department Faculty')`: Returns the faculty's name, or falls back to `'Department Faculty'` if the subject has no assigned instructor (`NULL`).
- Multi-predicate filtering: filters by authenticated student (`e.user_id = ?`) and specific day (`t.day_of_week = ?`).

---

### Example 8: Live System KPI Aggregations
**Application Feature:** Admin high-level institutional overview statistics.  
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `get_admin_stats()`

```sql
-- 1. Total Student Count
SELECT COUNT(*) AS total_students FROM users WHERE role = 'student';

-- 2. Institutional Average Attendance Percentage
SELECT 
    ROUND(
        CAST(SUM(CASE WHEN status IN ('present', 'excused') THEN 1 ELSE 0 END) AS FLOAT) * 100.0 
        / NULLIF(COUNT(*), 0), 
        1
    ) AS institutional_average
FROM attendance_records;

-- 3. Total Outstanding Student Fees Across Institution
SELECT 
    COALESCE(SUM(amount - amount_paid), 0.0) AS total_pending_fees
FROM fee_records;
```

#### Clause Breakdown:
- Uses SQL standard aggregate functions (`COUNT`, `SUM`, `ROUND`).
- Demonstrates how business dashboards compute live metrics directly in the database rather than loading thousands of rows into Python memory.

---

### Example 9: Idempotent Data Insertion with `ON CONFLICT`
**Application Feature:** Faculty marks entry with automatic update if marks already exist.  
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `enter_marks()`

```sql
INSERT INTO marks (id, examination_id, enrollment_id, marks_obtained, is_absent, grade)
VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT (examination_id, enrollment_id) DO UPDATE SET
    marks_obtained = excluded.marks_obtained,
    is_absent = excluded.is_absent,
    grade = excluded.grade;
```

#### Clause Breakdown:
- `ON CONFLICT (examination_id, enrollment_id)`: Leverages the composite `UNIQUE(examination_id, enrollment_id)` constraint defined in `001_simple_schema.sql`.
- `DO UPDATE SET ...`: Performs an "Upsert" (Insert or Update). If a mark already exists for this student in this exam, it updates the record instead of raising an integrity error.

---

### Example 10: Role-Based Circular Filtering with Pagination
**Application Feature:** Campus circulars notice board.  
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `get_notices()`

```sql
SELECT 
    n.id,
    n.title,
    n.category,
    n.content,
    COALESCE(u.name, 'Administration') AS published_by_name,
    n.is_published,
    n.target_role,
    n.published_at
FROM notices n
LEFT JOIN users u ON u.id = n.published_by
WHERE n.is_published = TRUE
  AND (n.target_role = 'all' OR n.target_role = ?)
ORDER BY n.published_at DESC
LIMIT ?;
```

#### Clause Breakdown:
- Role condition: `WHERE n.is_published = TRUE AND (n.target_role = 'all' OR n.target_role = ?)`. Only fetches circulars relevant to students or the entire institution.
- `ORDER BY n.published_at DESC LIMIT ?`: Orders by publication date descending with parameterized limit.

---

### Example 11: Multi-Filter Search with Parameterized `LIKE`
**Application Feature:** Search Information module (academic syllabus, timetables, fee FAQs, and exam schemes).
**Code Reference:** `backend/app/repositories/sql_repository.py` -> `search_information()`

```sql
SELECT
    id,
    branch,
    year,
    category,
    subject,
    title,
    content_details,
    file_url,
    created_at
FROM search_information
WHERE LOWER(category) LIKE ?
  AND year = ?
  AND (LOWER(title) LIKE ? OR LOWER(content_details) LIKE ? OR LOWER(subject) LIKE ?)
ORDER BY year ASC, category ASC, id ASC;
```

#### Clause Breakdown:
- Flexible pattern matching: `LOWER(category) LIKE ?` (with `'%syllabus%'` etc.) enables robust keyword filtering without brittle exact-casing requirements.
- Exact criteria: `year = ?` for direct academic year matching.
- Multi-field search: `(LOWER(title) LIKE ? OR LOWER(content_details) LIKE ? OR LOWER(subject) LIKE ?)` for safe free-text search across titles, subject names, and full-text descriptions.
- `ORDER BY year ASC, category ASC, id ASC`: Deterministic sorting providing stable ordering.

> **💡 Viva Defense Tip:**
> *"Why use parameterized LIKE queries instead of an external search engine? For college and enterprise portals, indexed SQL queries provide microsecond response times with zero external infrastructure, zero vector indexing cost, and 100% ANSI portability across SQLite and PostgreSQL."*

---

## 3. SQL Security & Best Practices

1. **Parameterization Everywhere**:  
   Every query executed in `backend/app/repositories/sql_repository.py` uses parameter markers (`?` in SQLite, `%s` in PostgreSQL). User input is never concatenated directly into SQL strings, completely neutralizing SQL Injection attacks.
2. **Defensive Zero-Division Guards**:  
   Every percentage calculation wraps divisors in `NULLIF(count, 0)` to guarantee SQL queries never throw division-by-zero runtime exceptions.
3. **Foreign Key Cascading**:  
   When an enrollment is deleted, child records in `attendance_records`, `marks`, and `fee_records` automatically cascade (`ON DELETE CASCADE`), preserving relational consistency.
