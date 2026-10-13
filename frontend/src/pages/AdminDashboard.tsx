import React, { useEffect, useState } from 'react';
import {
  Profile,
  StudentRosterItem,
  FacultyCourseAssignment,
  Notice,
  NoticeCategory,
} from '../types';
import { api } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { Alert } from '../components/common/Alert';
import {
  Users,
  Megaphone,
  BookOpen,
  ClipboardCheck,
  Search,
  Plus,
  Trash2,
  AlertTriangle,
  GraduationCap,
} from 'lucide-react';

interface AdminDashboardProps {
  currentUser: Profile | null;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ currentUser }) => {
  const [activeTab, setActiveTab] = useState<'roster' | 'notices' | 'assignments' | 'entry'>('roster');
  const [students, setStudents] = useState<StudentRosterItem[]>([]);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [facultyAssignments, setFacultyAssignments] = useState<FacultyCourseAssignment[]>([]);
  const [searchRoster, setSearchRoster] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // Modal states
  const [isAddStudentOpen, setIsAddStudentOpen] = useState(false);
  const [newStudent, setNewStudent] = useState({
    full_name: '',
    email: '',
    roll_number: '',
    program: 'B.Tech CSE',
    semester: 6,
    section: 'A',
    department: 'Computer Science',
  });

  // Notice form
  const [noticeForm, setNoticeForm] = useState({
    title: '',
    category: 'academic' as NoticeCategory,
    target_role: 'all' as 'all' | 'student' | 'faculty',
    content: '',
  });
  const [noticePublishSuccess, setNoticePublishSuccess] = useState(false);

  // Batch attendance simulator
  const [attendanceSubject, setAttendanceSubject] = useState('CS401');
  const [attendanceBatchStatus, setAttendanceBatchStatus] = useState<'present' | 'absent'>('present');
  const [entryMessage, setEntryMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadAdminData() {
      try {
        const [rosterData, noticeData, facultyData] = await Promise.all([
          api.getStudentRoster(),
          api.getNotices(),
          api.getFacultyAssignments(),
        ]);
        setStudents(rosterData);
        setNotices(noticeData);
        setFacultyAssignments(facultyData);
      } catch (err) {
        console.error('Failed to load admin data:', err);
      }
    }
    loadAdminData();
  }, []);

  // Filtered students
  const filteredStudents = students.filter((s) => {
    const matchStatus = statusFilter === 'all' || s.status === statusFilter;
    const matchSearch =
      s.full_name.toLowerCase().includes(searchRoster.toLowerCase()) ||
      s.roll_number.toLowerCase().includes(searchRoster.toLowerCase()) ||
      s.email.toLowerCase().includes(searchRoster.toLowerCase());
    return matchStatus && matchSearch;
  });

  const handleAddStudentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newStudent.full_name || !newStudent.roll_number) return;
    const added = await api.addStudent(newStudent);
    setStudents([added, ...students]);
    setIsAddStudentOpen(false);
    setNewStudent({
      full_name: '',
      email: '',
      roll_number: '',
      program: 'B.Tech CSE',
      semester: 6,
      section: 'A',
      department: 'Computer Science',
    });
  };

  const handlePublishNoticeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noticeForm.title || !noticeForm.content) return;
    const published = await api.publishNotice(noticeForm);
    setNotices([published, ...notices]);
    setNoticeForm({
      title: '',
      category: 'academic',
      target_role: 'all',
      content: '',
    });
    setNoticePublishSuccess(true);
    setTimeout(() => setNoticePublishSuccess(false), 3000);
  };

  const handleDeleteNotice = async (id: string) => {
    await api.deleteNotice(id);
    setNotices(notices.filter((n) => n.id !== id));
  };

  const handleBatchAttendanceEntry = async () => {
    const payload = students.map((s) => ({
      student_id: s.student_id,
      status: attendanceBatchStatus,
      subject_id: attendanceSubject,
    }));
    await api.recordAttendanceBatch(payload);
    setEntryMessage(
      `Successfully recorded attendance session for ${attendanceSubject} (${students.length} students marked ${attendanceBatchStatus.toUpperCase()})`
    );
    setTimeout(() => setEntryMessage(null), 4000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Admin Profile & Summary Banner */}
      <Card className="p-6 md:p-8 bg-gradient-to-r from-slate-900/90 via-indigo-950/40 to-slate-900/90 border border-white/10">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-indigo-600/30 border border-indigo-400/30 flex items-center justify-center text-indigo-300">
              <GraduationCap className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-white">
                  Academic Management Control Panel
                </h1>
                <Badge variant="danger" size="sm">
                  Super Administrator
                </Badge>
              </div>
              <p className="text-sm text-slate-400 mt-0.5">
                Logged in as <strong>{currentUser?.full_name || 'Dr. Raymond Holt'}</strong> • Office of Academic Affairs
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-4 py-2 rounded-xl bg-slate-900/60 border border-white/5 text-right">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">Enrolled Students</span>
              <span className="text-lg font-bold text-white font-mono">{students.length} Total</span>
            </div>
            <div className="px-4 py-2 rounded-xl bg-slate-900/60 border border-white/5 text-right">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">Published Notices</span>
              <span className="text-lg font-bold text-indigo-400 font-mono">{notices.length} Active</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-white/10 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('roster')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'roster'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Student Roster</span>
        </button>

        <button
          onClick={() => setActiveTab('notices')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'notices'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Megaphone className="w-4 h-4" />
          <span>Notice Publisher</span>
        </button>

        <button
          onClick={() => setActiveTab('assignments')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'assignments'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>Faculty Assignments</span>
        </button>

        <button
          onClick={() => setActiveTab('entry')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'entry'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <ClipboardCheck className="w-4 h-4" />
          <span>Attendance & Marks Entry</span>
        </button>
      </div>

      {/* Tab 1: Student Roster */}
      {activeTab === 'roster' && (
        <Card className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-white">Student Directory & Academic Health</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Inspect enrollment standing, aggregate attendance percentages, and GPA metrics
              </p>
            </div>
            <Button
              variant="primary"
              size="sm"
              icon={<Plus className="w-4 h-4" />}
              onClick={() => setIsAddStudentOpen(true)}
            >
              Enroll Student
            </Button>
          </div>

          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchRoster}
                onChange={(e) => setSearchRoster(e.target.value)}
                placeholder="Search students by roll number or name..."
                className="w-full pl-10 pr-4 py-2 rounded-xl glass-input text-sm"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="glass-input rounded-xl px-3 py-2 text-sm text-slate-200 outline-none w-full sm:w-auto"
            >
              <option value="all" className="bg-slate-900">All Statuses</option>
              <option value="active" className="bg-slate-900">Active</option>
              <option value="suspended" className="bg-slate-900">Suspended</option>
            </select>
          </div>

          {/* Table */}
          <div className="overflow-x-auto rounded-xl border border-white/5 bg-slate-900/40">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-white/10 bg-slate-800/40 text-slate-400 text-xs uppercase font-mono">
                  <th className="py-3 px-4 font-semibold">Student & Roll No</th>
                  <th className="py-3 px-4 font-semibold">Program & Section</th>
                  <th className="py-3 px-4 font-semibold text-center">Attendance %</th>
                  <th className="py-3 px-4 font-semibold text-center">CGPA</th>
                  <th className="py-3 px-4 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredStudents.map((s) => {
                  const isLow = s.attendance_percentage < 75;
                  return (
                    <tr key={s.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-white">{s.full_name}</div>
                        <div className="text-xs font-mono text-indigo-300">{s.roll_number}</div>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="text-slate-200">{s.program}</div>
                        <div className="text-xs text-slate-400">
                          Sem {s.semester} (Sec {s.section})
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <div className="flex items-center justify-center gap-1.5">
                          {isLow && <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
                          <span
                            className={`font-mono font-bold ${
                              isLow ? 'text-rose-400' : 'text-emerald-400'
                            }`}
                          >
                            {s.attendance_percentage.toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center font-mono font-semibold text-slate-200">
                        {s.gpa.toFixed(2)}
                      </td>
                      <td className="py-3.5 px-4">
                        <Badge
                          variant={s.status === 'active' ? 'success' : 'danger'}
                          size="sm"
                        >
                          {s.status.toUpperCase()}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Tab 2: Notice Publisher */}
      {activeTab === 'notices' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-5">
            <Card className="space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Megaphone className="w-5 h-5 text-indigo-400" />
                Publish Institutional Circular
              </h3>

              {noticePublishSuccess && (
                <Alert variant="success" title="Published Successfully">
                  Notice is now visible to the student and faculty portals.
                </Alert>
              )}

              <form onSubmit={handlePublishNoticeSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Notice Title
                  </label>
                  <input
                    type="text"
                    required
                    value={noticeForm.title}
                    onChange={(e) => setNoticeForm({ ...noticeForm, title: e.target.value })}
                    placeholder="e.g. Schedule for Mid-Term Make-up Exams"
                    className="w-full glass-input rounded-xl px-3.5 py-2 text-sm"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Category
                    </label>
                    <select
                      value={noticeForm.category}
                      onChange={(e) =>
                        setNoticeForm({ ...noticeForm, category: e.target.value as NoticeCategory })
                      }
                      className="w-full glass-input rounded-xl px-3 py-2 text-sm text-slate-200 outline-none"
                    >
                      <option value="academic" className="bg-slate-900">Academic</option>
                      <option value="examination" className="bg-slate-900">Examination</option>
                      <option value="urgent" className="bg-slate-900">Urgent</option>
                      <option value="administrative" className="bg-slate-900">Administrative</option>
                      <option value="event" className="bg-slate-900">Campus Event</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Audience
                    </label>
                    <select
                      value={noticeForm.target_role}
                      onChange={(e) =>
                        setNoticeForm({
                          ...noticeForm,
                          target_role: e.target.value as 'all' | 'student' | 'faculty',
                        })
                      }
                      className="w-full glass-input rounded-xl px-3 py-2 text-sm text-slate-200 outline-none"
                    >
                      <option value="all" className="bg-slate-900">All (University-wide)</option>
                      <option value="student" className="bg-slate-900">Students Only</option>
                      <option value="faculty" className="bg-slate-900">Faculty Only</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Announcement Body
                  </label>
                  <textarea
                    rows={4}
                    required
                    value={noticeForm.content}
                    onChange={(e) => setNoticeForm({ ...noticeForm, content: e.target.value })}
                    placeholder="Type official circular content here..."
                    className="w-full glass-input rounded-xl px-3.5 py-2 text-sm"
                  />
                </div>

                <Button type="submit" variant="primary" className="w-full">
                  Broadcast Notice
                </Button>
              </form>
            </Card>
          </div>

          <div className="lg:col-span-7">
            <Card className="space-y-4">
              <h3 className="text-lg font-bold text-white">Active Notices Archive</h3>
              <div className="space-y-3">
                {notices.map((n) => (
                  <div
                    key={n.id}
                    className="p-4 rounded-xl bg-slate-800/40 border border-white/5 flex items-start justify-between gap-3"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="neutral" size="sm">{n.category.toUpperCase()}</Badge>
                        <span className="text-xs text-slate-400 font-mono">{n.published_at.substring(0, 10)}</span>
                      </div>
                      <h4 className="text-sm font-semibold text-white">{n.title}</h4>
                      <p className="text-xs text-slate-400 line-clamp-2">{n.content}</p>
                    </div>

                    <button
                      onClick={() => handleDeleteNotice(n.id)}
                      className="p-2 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                      title="Delete Notice"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Tab 3: Faculty Assignments */}
      {activeTab === 'assignments' && (
        <Card className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-white">Faculty Course Allotments</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Active semester subject teaching assignments and student enrollments
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {facultyAssignments.map((fca) => (
              <div
                key={fca.id}
                className="p-5 rounded-xl bg-slate-800/40 border border-white/5 hover:border-indigo-500/30 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/20">
                      {fca.subject_code}
                    </span>
                    <Badge variant="primary" size="sm">
                      {fca.course_section}
                    </Badge>
                  </div>
                  <h4 className="text-base font-bold text-white">{fca.subject_name}</h4>
                  <p className="text-sm text-slate-300 mt-1 font-medium">
                    Instructor: {fca.faculty_name}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs text-slate-400 font-mono">
                  <span>Enrolled Candidates:</span>
                  <span className="font-bold text-emerald-400">{fca.enrolled_count} Students</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Tab 4: Attendance & Marks Quick Entry Simulator */}
      {activeTab === 'entry' && (
        <Card className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-white">Batch Academic Ledger Entry</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Record attendance sessions or submit grade ledger modifications with transaction commit
            </p>
          </div>

          {entryMessage && (
            <Alert variant="success" title="Ledger Updated">
              {entryMessage}
            </Alert>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Attendance Entry Card */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-white/10 space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <ClipboardCheck className="w-5 h-5 text-indigo-400" />
                Mark Daily Class Session Attendance
              </h3>

              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Select Subject Offering
                  </label>
                  <select
                    value={attendanceSubject}
                    onChange={(e) => setAttendanceSubject(e.target.value)}
                    className="w-full glass-input rounded-xl px-3 py-2 text-sm text-slate-200 outline-none"
                  >
                    <option value="CS401" className="bg-slate-900">CS401 - Cloud Computing</option>
                    <option value="CS402" className="bg-slate-900">CS402 - Machine Learning</option>
                    <option value="CS403" className="bg-slate-900">CS403 - Database Engineering</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Batch Status Setting
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => setAttendanceBatchStatus('present')}
                      className={`p-2.5 rounded-xl text-xs font-semibold transition-all ${
                        attendanceBatchStatus === 'present'
                          ? 'bg-emerald-600 text-white shadow-md'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      All Present
                    </button>
                    <button
                      type="button"
                      onClick={() => setAttendanceBatchStatus('absent')}
                      className={`p-2.5 rounded-xl text-xs font-semibold transition-all ${
                        attendanceBatchStatus === 'absent'
                          ? 'bg-rose-600 text-white shadow-md'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      Mark Absences
                    </button>
                  </div>
                </div>

                <Button
                  variant="primary"
                  className="w-full mt-2"
                  onClick={handleBatchAttendanceEntry}
                >
                  Commit Attendance Session
                </Button>
              </div>
            </div>

            {/* Marks Assessment Entry */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-white/10 space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-indigo-400" />
                Submit Evaluation Marks
              </h3>

              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Evaluation Category
                  </label>
                  <input
                    type="text"
                    defaultValue="End-Semester Examination Autumn 2026"
                    className="w-full glass-input rounded-xl px-3.5 py-2 text-sm text-slate-200"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Maximum Scale Marks
                  </label>
                  <input
                    type="number"
                    defaultValue="100"
                    className="w-full glass-input rounded-xl px-3.5 py-2 text-sm text-slate-200 font-mono"
                  />
                </div>

                <Button
                  variant="secondary"
                  className="w-full mt-2"
                  onClick={() => {
                    setEntryMessage('Evaluation component initialized and open for faculty marks submission.');
                    setTimeout(() => setEntryMessage(null), 4000);
                  }}
                >
                  Open Examination Ledger
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Add Student Modal */}
      {isAddStudentOpen && (
        <Modal
          isOpen={isAddStudentOpen}
          onClose={() => setIsAddStudentOpen(false)}
          title="Enroll New Student to Academic Register"
        >
          <form onSubmit={handleAddStudentSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Full Legal Name
              </label>
              <input
                type="text"
                required
                value={newStudent.full_name}
                onChange={(e) => setNewStudent({ ...newStudent, full_name: e.target.value })}
                placeholder="e.g. Jordan Lee"
                className="w-full glass-input rounded-xl px-3.5 py-2 text-sm"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Roll Number
                </label>
                <input
                  type="text"
                  required
                  value={newStudent.roll_number}
                  onChange={(e) => setNewStudent({ ...newStudent, roll_number: e.target.value })}
                  placeholder="CS2023-0490"
                  className="w-full glass-input rounded-xl px-3.5 py-2 text-sm font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Section
                </label>
                <select
                  value={newStudent.section}
                  onChange={(e) => setNewStudent({ ...newStudent, section: e.target.value })}
                  className="w-full glass-input rounded-xl px-3 py-2 text-sm text-slate-200 outline-none"
                >
                  <option value="A" className="bg-slate-900">Section A</option>
                  <option value="B" className="bg-slate-900">Section B</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Institutional Email
              </label>
              <input
                type="email"
                required
                value={newStudent.email}
                onChange={(e) => setNewStudent({ ...newStudent, email: e.target.value })}
                placeholder="jordan.lee@university.edu"
                className="w-full glass-input rounded-xl px-3.5 py-2 text-sm"
              />
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setIsAddStudentOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                Confirm Enrollment
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
