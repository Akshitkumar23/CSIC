export type UserRole = 'student' | 'faculty' | 'admin';

export interface Profile {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string;
  avatar_url?: string;
  roll_number?: string;
  department?: string;
  program?: string;
  semester?: number;
  section?: string;
  is_active?: boolean;
}

export interface SubjectAttendance {
  subject_id?: string;
  subject_code: string;
  subject_name: string;
  faculty_name?: string;
  total_sessions?: number;
  conducted_classes?: number;
  attended_sessions?: number;
  attended_classes?: number;
  excused_sessions?: number;
  excused_classes?: number;
  absent_sessions?: number;
  attendance_percentage?: number;
  percentage?: number;
  is_low_attendance?: boolean;
  status_warning?: boolean;
  classes_needed_for_75?: number;
}

export interface AttendanceSummary {
  student_id?: string;
  roll_number?: string;
  overall_percentage: number;
  is_at_risk?: boolean;
  total_conducted?: number;
  total_attended?: number;
  total_excused?: number;
  low_attendance_warning?: boolean;
  classes_needed_to_reach_threshold?: number;
  subjects: SubjectAttendance[];
}

export interface Mark {
  id: string;
  subject_id: string;
  subject_code: string;
  subject_name: string;
  exam_name: string;
  exam_date: string;
  marks_obtained: number;
  max_marks: number;
  percentage: number;
  grade: string;
  is_absent: boolean;
  weightage?: number;
}

export interface FeeInvoice {
  id: string;
  invoice_number: string;
  title: string;
  amount: number;
  due_date: string;
  status: 'paid' | 'unpaid' | 'partially_paid' | 'overdue' | 'cancelled';
  paid_amount?: number;
  payment_date?: string;
  transaction_ref?: string;
}

export type DayOfWeek = 'Monday' | 'Tuesday' | 'Wednesday' | 'Thursday' | 'Friday' | 'Saturday';

export interface TimetableEntry {
  id: string;
  day_of_week: DayOfWeek;
  start_time: string;
  end_time: string;
  subject_code: string;
  subject_name: string;
  room_number: string;
  faculty_name: string;
  course_section?: string;
}

export type NoticeCategory = 'academic' | 'examination' | 'administrative' | 'fees' | 'event' | 'urgent';

export interface Notice {
  id: string;
  title: string;
  category: NoticeCategory;
  content: string;
  published_by_name: string;
  published_at: string;
  target_role: 'all' | 'student' | 'faculty';
  is_urgent?: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message_preview?: string;
}

export interface ChatMessage {
  id: string;
  session_id?: string;
  sender: 'user' | 'bot' | 'system';
  text: string;
  timestamp: string;
  query_type?: 'attendance' | 'marks' | 'fees' | 'timetable' | 'notices' | 'policy_document' | 'rag_document' | 'general' | 'unsupported';
  sources?: string[];
  verified_data?: Record<string, any>;
}

export interface StudentRosterItem {
  id: string;
  student_id: string;
  full_name: string;
  email: string;
  roll_number: string;
  department: string;
  program: string;
  semester: number;
  section: string;
  status: 'active' | 'completed' | 'dropped' | 'suspended';
  attendance_percentage: number;
  gpa: number;
}

export interface FacultyCourseAssignment {
  id: string;
  faculty_id: string;
  faculty_name: string;
  subject_id: string;
  subject_code: string;
  subject_name: string;
  course_section: string;
  enrolled_count: number;
}

export interface AuthResponse {
  token: string;
  user: Profile;
}

export interface FeePayment {
  id: string;
  invoice_id: string;
  transaction_reference: string;
  amount_paid: number;
  payment_date: string;
  payment_method: string;
  status: string;
}

export interface AttendanceWarning {
  student_id: string;
  student_name: string;
  roll_number: string;
  overall_percentage: number;
  at_risk_subjects: string[];
}
