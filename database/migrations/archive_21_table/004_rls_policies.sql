-- ==============================================================================
-- Cloud-Based Student Information Chatbot (CSIC)
-- Migration: 004_rls_policies.sql
-- Description: Comprehensive Row-Level Security (RLS) for Student, Faculty & Admin
-- Compliance: PostgreSQL 15+, Supabase Auth, Multi-Tenant Role Isolation
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Helper Functions to Resolve Identity and Role
-- ------------------------------------------------------------------------------

-- Returns the authenticated user's UUID from Supabase auth or session configuration
CREATE OR REPLACE FUNCTION current_app_user_id() RETURNS UUID AS $$
BEGIN
    -- 1. Check Supabase auth.uid() function if available
    BEGIN
        IF auth.uid() IS NOT NULL THEN
            RETURN auth.uid();
        END IF;
    EXCEPTION
        WHEN undefined_function THEN NULL;
    END;

    -- 2. Check JWT sub claim
    IF current_setting('request.jwt.claim.sub', true) IS NOT NULL 
       AND current_setting('request.jwt.claim.sub', true) <> '' THEN
        RETURN current_setting('request.jwt.claim.sub', true)::UUID;
    END IF;

    -- 3. Check session testing setting
    IF current_setting('app.current_user_id', true) IS NOT NULL 
       AND current_setting('app.current_user_id', true) <> '' THEN
        RETURN current_setting('app.current_user_id', true)::UUID;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Returns the authenticated user's role ('admin', 'faculty', 'student')
CREATE OR REPLACE FUNCTION current_app_user_role() RETURNS TEXT AS $$
DECLARE
    v_role TEXT;
BEGIN
    -- 1. Check explicit session override if set
    IF current_setting('app.current_user_role', true) IS NOT NULL 
       AND current_setting('app.current_user_role', true) <> '' THEN
        RETURN current_setting('app.current_user_role', true);
    END IF;

    -- 2. Lookup role from profiles table
    SELECT role INTO v_role 
    FROM profiles 
    WHERE id = current_app_user_id();

    RETURN v_role;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- ==============================================================================
-- 2. Enable Row-Level Security (RLS) on All Sensitive Entities
-- ==============================================================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_years ENABLE ROW LEVEL SECURITY;
ALTER TABLE semesters ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE faculty_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE class_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE examinations ENABLE ROW LEVEL SECURITY;
ALTER TABLE marks ENABLE ROW LEVEL SECURITY;
ALTER TABLE fee_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE fee_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE timetable_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE notices ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ==============================================================================
-- 3. Public / Academic Catalog Read Access (Common to all authenticated users)
-- ==============================================================================

-- Departments, Programs, Academic Years, Semesters, Courses, Subjects
CREATE POLICY departments_read_all ON departments FOR SELECT TO PUBLIC USING (TRUE);
CREATE POLICY programs_read_all ON programs FOR SELECT TO PUBLIC USING (TRUE);
CREATE POLICY academic_years_read_all ON academic_years FOR SELECT TO PUBLIC USING (TRUE);
CREATE POLICY semesters_read_all ON semesters FOR SELECT TO PUBLIC USING (TRUE);
CREATE POLICY courses_read_all ON courses FOR SELECT TO PUBLIC USING (TRUE);
CREATE POLICY subjects_read_all ON subjects FOR SELECT TO PUBLIC USING (TRUE);
CREATE POLICY faculty_assignments_read_all ON faculty_assignments FOR SELECT TO PUBLIC USING (TRUE);
CREATE POLICY documents_read_all ON documents FOR SELECT TO PUBLIC USING (TRUE);
CREATE POLICY document_chunks_read_all ON document_chunks FOR SELECT TO PUBLIC USING (TRUE);

-- ==============================================================================
-- 4. Admin Role Policies (Full Unrestricted Access to All Tables)
-- ==============================================================================

CREATE POLICY admin_all_profiles ON profiles FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_departments ON departments FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_programs ON programs FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_academic_years ON academic_years FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_semesters ON semesters FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_courses ON courses FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_subjects ON subjects FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_faculty_assignments ON faculty_assignments FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_enrollments ON enrollments FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_class_sessions ON class_sessions FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_attendance_records ON attendance_records FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_examinations ON examinations FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_marks ON marks FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_fee_invoices ON fee_invoices FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_fee_payments ON fee_payments FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_timetable_entries ON timetable_entries FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_notices ON notices FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_documents ON documents FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_document_chunks ON document_chunks FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_chat_sessions ON chat_sessions FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_chat_messages ON chat_messages FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

CREATE POLICY admin_all_audit_logs ON audit_logs FOR ALL TO PUBLIC
    USING (current_app_user_role() = 'admin') WITH CHECK (current_app_user_role() = 'admin');

-- ==============================================================================
-- 5. Student Role Policies (Access Strictly Scoped to Own Identity)
-- ==============================================================================

-- Profiles: Student can view own profile and faculty profiles (to identify instructors)
CREATE POLICY student_select_profiles ON profiles FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student' 
        AND (id = current_app_user_id() OR role = 'faculty')
    );

CREATE POLICY student_update_own_profile ON profiles FOR UPDATE TO PUBLIC
    USING (current_app_user_role() = 'student' AND id = current_app_user_id())
    WITH CHECK (current_app_user_role() = 'student' AND id = current_app_user_id());

-- Enrollments: Student views only their own enrollments
CREATE POLICY student_select_own_enrollments ON enrollments FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student' 
        AND student_id = current_app_user_id()
    );

-- Class Sessions: Student views sessions for courses they are enrolled in
CREATE POLICY student_select_course_sessions ON class_sessions FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student'
        AND faculty_assignment_id IN (
            SELECT fa.id 
            FROM faculty_assignments fa
            JOIN enrollments e ON e.course_id = fa.course_id
            WHERE e.student_id = current_app_user_id()
        )
    );

-- Attendance: Student views ONLY their own attendance records
CREATE POLICY student_select_own_attendance ON attendance_records FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student'
        AND enrollment_id IN (
            SELECT id FROM enrollments WHERE student_id = current_app_user_id()
        )
    );

-- Examinations: Student views examinations scheduled for their course
CREATE POLICY student_select_course_examinations ON examinations FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student'
        AND course_id IN (
            SELECT course_id FROM enrollments WHERE student_id = current_app_user_id()
        )
    );

-- Marks: Student views ONLY their own marks
CREATE POLICY student_select_own_marks ON marks FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student'
        AND enrollment_id IN (
            SELECT id FROM enrollments WHERE student_id = current_app_user_id()
        )
    );

-- Invoices & Payments: Student views ONLY their own fee records
CREATE POLICY student_select_own_invoices ON fee_invoices FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student'
        AND enrollment_id IN (
            SELECT id FROM enrollments WHERE student_id = current_app_user_id()
        )
    );

CREATE POLICY student_select_own_payments ON fee_payments FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student'
        AND invoice_id IN (
            SELECT fi.id 
            FROM fee_invoices fi
            JOIN enrollments e ON fi.enrollment_id = e.id
            WHERE e.student_id = current_app_user_id()
        )
    );

-- Timetable: Student views timetable entries for courses they are enrolled in
CREATE POLICY student_select_course_timetable ON timetable_entries FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student'
        AND faculty_assignment_id IN (
            SELECT fa.id 
            FROM faculty_assignments fa
            JOIN enrollments e ON e.course_id = fa.course_id
            WHERE e.student_id = current_app_user_id()
        )
    );

-- Notices: Student views published notices targeting 'all' or 'student'
CREATE POLICY student_select_published_notices ON notices FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student'
        AND is_published = TRUE
        AND target_role IN ('all', 'student')
    );

-- Chat Sessions & Messages: Student has full CRUD on own conversations
CREATE POLICY student_manage_own_chat_sessions ON chat_sessions FOR ALL TO PUBLIC
    USING (
        current_app_user_role() = 'student' 
        AND student_id = current_app_user_id()
    )
    WITH CHECK (
        current_app_user_role() = 'student' 
        AND student_id = current_app_user_id()
    );

CREATE POLICY student_manage_own_chat_messages ON chat_messages FOR ALL TO PUBLIC
    USING (
        current_app_user_role() = 'student'
        AND session_id IN (
            SELECT id FROM chat_sessions WHERE student_id = current_app_user_id()
        )
    )
    WITH CHECK (
        current_app_user_role() = 'student'
        AND session_id IN (
            SELECT id FROM chat_sessions WHERE student_id = current_app_user_id()
        )
    );

-- Audit Logs: Student views only their own audit footprint
CREATE POLICY student_select_own_audit ON audit_logs FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'student'
        AND actor_id = current_app_user_id()
    );

-- ==============================================================================
-- 6. Faculty Role Policies (Scoped to Assigned Courses and Teaching Duties)
-- ==============================================================================

-- Profiles: Faculty can view all student and faculty profiles
CREATE POLICY faculty_select_profiles ON profiles FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'faculty'
        AND role IN ('student', 'faculty')
    );

CREATE POLICY faculty_update_own_profile ON profiles FOR UPDATE TO PUBLIC
    USING (current_app_user_role() = 'faculty' AND id = current_app_user_id())
    WITH CHECK (current_app_user_role() = 'faculty' AND id = current_app_user_id());

-- Enrollments: Faculty can view enrollments in courses they teach
CREATE POLICY faculty_select_course_enrollments ON enrollments FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'faculty'
        AND course_id IN (
            SELECT course_id FROM faculty_assignments WHERE faculty_id = current_app_user_id()
        )
    );

-- Class Sessions: Faculty can view and conduct sessions for their assigned subjects
CREATE POLICY faculty_manage_assigned_sessions ON class_sessions FOR ALL TO PUBLIC
    USING (
        current_app_user_role() = 'faculty'
        AND faculty_assignment_id IN (
            SELECT id FROM faculty_assignments WHERE faculty_id = current_app_user_id()
        )
    )
    WITH CHECK (
        current_app_user_role() = 'faculty'
        AND faculty_assignment_id IN (
            SELECT id FROM faculty_assignments WHERE faculty_id = current_app_user_id()
        )
    );

-- Attendance: Faculty can record and update attendance for their conducted sessions
CREATE POLICY faculty_manage_session_attendance ON attendance_records FOR ALL TO PUBLIC
    USING (
        current_app_user_role() = 'faculty'
        AND session_id IN (
            SELECT cs.id 
            FROM class_sessions cs
            JOIN faculty_assignments fa ON cs.faculty_assignment_id = fa.id
            WHERE fa.faculty_id = current_app_user_id()
        )
    )
    WITH CHECK (
        current_app_user_role() = 'faculty'
        AND session_id IN (
            SELECT cs.id 
            FROM class_sessions cs
            JOIN faculty_assignments fa ON cs.faculty_assignment_id = fa.id
            WHERE fa.faculty_id = current_app_user_id()
        )
    );

-- Examinations: Faculty can manage examinations for their assigned subjects
CREATE POLICY faculty_manage_subject_examinations ON examinations FOR ALL TO PUBLIC
    USING (
        current_app_user_role() = 'faculty'
        AND (course_id, subject_id) IN (
            SELECT course_id, subject_id 
            FROM faculty_assignments 
            WHERE faculty_id = current_app_user_id()
        )
    )
    WITH CHECK (
        current_app_user_role() = 'faculty'
        AND (course_id, subject_id) IN (
            SELECT course_id, subject_id 
            FROM faculty_assignments 
            WHERE faculty_id = current_app_user_id()
        )
    );

-- Marks: Faculty can enter and update marks for exams in their subjects
CREATE POLICY faculty_manage_subject_marks ON marks FOR ALL TO PUBLIC
    USING (
        current_app_user_role() = 'faculty'
        AND examination_id IN (
            SELECT ex.id 
            FROM examinations ex
            JOIN faculty_assignments fa 
              ON fa.course_id = ex.course_id AND fa.subject_id = ex.subject_id
            WHERE fa.faculty_id = current_app_user_id()
        )
    )
    WITH CHECK (
        current_app_user_role() = 'faculty'
        AND examination_id IN (
            SELECT ex.id 
            FROM examinations ex
            JOIN faculty_assignments fa 
              ON fa.course_id = ex.course_id AND fa.subject_id = ex.subject_id
            WHERE fa.faculty_id = current_app_user_id()
        )
    );

-- Timetable: Faculty can view all institutional timetable entries
CREATE POLICY faculty_select_timetable ON timetable_entries FOR SELECT TO PUBLIC
    USING (current_app_user_role() = 'faculty');

-- Notices: Faculty can view published notices and author/manage their own notices
CREATE POLICY faculty_select_notices ON notices FOR SELECT TO PUBLIC
    USING (
        current_app_user_role() = 'faculty'
        AND (
            (is_published = TRUE AND target_role IN ('all', 'faculty'))
            OR published_by = current_app_user_id()
        )
    );

CREATE POLICY faculty_insert_notices ON notices FOR INSERT TO PUBLIC
    WITH CHECK (
        current_app_user_role() = 'faculty'
        AND published_by = current_app_user_id()
    );

CREATE POLICY faculty_update_own_notices ON notices FOR UPDATE TO PUBLIC
    USING (
        current_app_user_role() = 'faculty'
        AND published_by = current_app_user_id()
    )
    WITH CHECK (
        current_app_user_role() = 'faculty'
        AND published_by = current_app_user_id()
    );
