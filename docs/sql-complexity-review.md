# SQL Complexity Audit & Simplification Review

**Date:** 2026-10-13  
**Objective:** Audit all SQL constructs across migrations, views, indexes, tests, and documentation. Align the repository with the educational objective: **Practical Cloud Computing and Basic-to-Intermediate Relational SQL**, eliminating gratuitous complexity while preserving data integrity, security, and functionality.

---

## 1. Summary of SQL Complexity Audit

| SQL Construct / Pattern | Location(s) Found | Original Purpose | Assessment | Recommendation & Simpler Equivalent |
| :--- | :--- | :--- | :--- | :--- |
| **Multi-Stage Common Table Expressions (3-Level CTE Chain)** | `docs/sql/demonstrations.md` (§5.1) | Composite Academic Risk calculation chaining AttendanceAggregates -> MarksAggregates -> CompositeRiskScore. | **Unnecessarily Complex for Core Learning.** Overwhelms students without adding features used in the app. | **Simplify in Learning Guide.** Replace with simple, standalone subqueries or a clean 2-table query with standard joins. Keep CTEs to simple, single-level `WITH summary AS (...)` examples. |
| **Window Functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`)** | `docs/sql/demonstrations.md` (§6.1, §6.2), `database/test_schema.py` | Cohort rank calculation and exam-to-exam score progression. | **Educational Extension Only.** None of the 10 core reporting views actually require window functions! | **Retain as clearly labeled "Optional Advanced Topic" in docs; do not make core application dependent on them.** Core views rely strictly on standard `GROUP BY` and aggregate functions. |
| **`EXTRACT(EPOCH FROM (end_time - start_time)) / 3600.0`** | `database/migrations/002_reporting_views.sql` (`v_faculty_workload`) | Computes teaching hours per week from `TIME` columns. | **PostgreSQL-Specific Date Arithmetic.** Can be confusing for beginners and behaves differently in SQLite. | **Retain in View with Clear Explanation.** In PostgreSQL, `(end_time - start_time)` yields an `INTERVAL`; extracting epoch converts seconds to hours. Document clearly in plain English. |
| **Conditional Aggregations: `COUNT(CASE WHEN ... THEN 1 END)`** | `002_reporting_views.sql` (`v_student_attendance`, `v_subject_performance_summary`, etc.) | Filters row counts within aggregate functions (e.g., counting only present sessions, or absent candidates). | **Essential & Best-Practice Relational SQL.** Standard ANSI SQL pattern for pivoting counts without multiple queries. | **Keep.** This is the standard, readable intermediate SQL pattern taught in university database courses. |
| **`NULLIF(COUNT(...), 0)` & `ROUND(...)`** | `002_reporting_views.sql` (`v_student_attendance`) | Prevents Division-by-Zero errors when a course has zero sessions conducted. | **Essential for Correctness.** Without `NULLIF`, dividing by zero causes fatal SQL runtime errors. | **Keep.** Clearly explain in viva prep as the standard technique to avoid `division by zero`. |
| **Mathematical Recovery Calculation: `CEIL(3*total - 4*attended)`** | `002_reporting_views.sql` (`v_low_attendance_warnings`) | Solves algebraic inequality $\frac{\text{attended} + x}{\text{total} + x} \ge 0.75 \implies x \ge 3 \cdot \text{total} - 4 \cdot \text{attended}$. | **Useful Domain Feature.** Gives students exact number of classes needed to clear 75%. | **Keep in View, Document Algebraic Derivation.** Simplifies student understanding by showing the simple algebra behind it. |
| **Correlated Subqueries vs Joins** | `002_reporting_views.sql` (`v_fee_outstanding_summary`) | Sums paid fees per enrollment. | **Appropriate Intermediate SQL.** Avoids multi-table Cartesian product when joining invoices and payments. | **Keep.** Demonstrates when a correlated subquery is cleaner than an aggregation over multiple 1:N joins. |
| **Composite Indexes (`session_id, enrollment_id`, `exam_id, enrollment_id`)** | `database/migrations/001_initial_schema.sql` | Fast lookup on multi-column foreign keys and uniqueness checks. | **Justified by Query Patterns.** Prevents duplicate attendance/marks entries. | **Keep.** Explain the Leftmost Prefix Rule in plain terms. |
| **HNSW Vector Index (`vector(768)`)** | `database/migrations/001_initial_schema.sql` (`document_chunks`) | Vector similarity search for RAG embeddings. | **Cloud AI Requirement.** Required by pgvector for semantic search. | **Keep, but isolate.** Document that this is specifically for AI retrieval and distinct from standard B-Tree relational indexing. |
| **Custom PL/pgSQL RLS Helper Functions** | `database/migrations/004_rls_policies.sql` (`current_app_user_id()`) | Reads JWT claims (`request.jwt.claim.sub`) for Supabase Row-Level Security. | **Required for Supabase Integration.** Standard pattern recommended by official Supabase security docs. | **Keep in Migrations.** Fully documented as the security bridge between HTTP tokens and PostgreSQL RLS. |

---

## 2. Core Relational Schema Retained (21 Tables in 3NF)

The schema integrity is preserved with clean Third Normal Form relationships:
1. **Identity & Catalogs:** `profiles`, `departments`, `programs`
2. **Academic Batches:** `academic_years`, `semesters`, `courses`, `subjects`, `faculty_assignments`
3. **Student Enrolment & Attendance:** `enrollments`, `class_sessions`, `attendance_records`
4. **Assessment & Grading:** `examinations`, `marks`
5. **Fee Management:** `fee_invoices`, `fee_payments`
6. **Schedules & Announcements:** `timetable_entries`, `notices`
7. **Institutional Knowledge & Chat:** `documents`, `document_chunks`, `chat_sessions`, `chat_messages`
8. **Operational Auditing:** `audit_logs`

All tables use standard primary keys (`id UUID`), foreign keys with explicit referential integrity (`ON DELETE RESTRICT` or `ON DELETE CASCADE`), `UNIQUE` constraints preventing duplicate records, and `CHECK` constraints enforcing allowed status values.

---

## 3. Recommended Basic-to-Intermediate SQL Learning Curriculum

For academic evaluation and student comprehension, SQL demonstrations in `docs/sql/demonstrations.md` are streamlined to focus on:
1. **Basic Queries:** `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`.
2. **Table Relationships:** `INNER JOIN` (filtering to matching rows) and `LEFT JOIN` (preserving parent records).
3. **Aggregations:** `COUNT(*)`, `SUM()`, `AVG()`, `MIN()`, `MAX()`.
4. **Group Summaries:** `GROUP BY` and filtering aggregates with `HAVING`.
5. **Conditional Logic:** `CASE WHEN ... THEN ... ELSE ... END`.
6. **Subqueries & Views:** Creating reusable reporting views (`CREATE VIEW`).
7. **Database Constraints & Indexes:** Primary keys, foreign keys, unique indexes, and performance rationale.
8. **Transactions:** `BEGIN`, `COMMIT`, `ROLLBACK` for financial fee payment integrity.
