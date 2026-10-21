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
  Search,
  Plus,
  Trash2,
  AlertTriangle,
  GraduationCap,
} from 'lucide-react';

interface AdminDashboardProps {
  currentUser: Profile | null;
}

export const AdminDashboardPage: React.FC<AdminDashboardProps> = ({ currentUser }) => {
  const [activeTab, setActiveTab] = useState<'roster' | 'notices' | 'assignments'>('roster');
  const [students, setStudents] = useState<StudentRosterItem[]>([]);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [facultyAssignments, setFacultyAssignments] = useState<FacultyCourseAssignment[]>([]);
  const [searchRoster, setSearchRoster] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // Modal states
  const [isAddStudentOpen, setIsAddStudentOpen] = useState(false);
  const [isAddingStudent, setIsAddingStudent] = useState(false);
  const [addStudentError, setAddStudentError] = useState<string | null>(null);
  const [newStudent, setNewStudent] = useState({
    full_name: '',
    email: '',
    roll_number: '',
    program_code: 'BTECH-CSE',
    semester: 6,
    section: 'A',
    password: 'Student@123',
  });

  // Notice form
  const [noticeForm, setNoticeForm] = useState({
    title: '',
    category: 'academic' as NoticeCategory,
    target_role: 'all' as 'all' | 'student' | 'faculty',
    content: '',
  });
  const [noticePublishSuccess, setNoticePublishSuccess] = useState(false);

  useEffect(() => {
    async function loadAdminData() {
      try {
        const [rosterRes, noticeRes, facultyRes] = await Promise.allSettled([
          api.getStudentRoster(),
          api.getNotices(),
          api.getFacultyAssignments(),
        ]);
        if (rosterRes.status === 'fulfilled') setStudents(rosterRes.value);
        if (noticeRes.status === 'fulfilled') setNotices(noticeRes.value);
        if (facultyRes.status === 'fulfilled') setFacultyAssignments(facultyRes.value);
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
    if (!newStudent.full_name || !newStudent.roll_number || !newStudent.email) return;
    setIsAddingStudent(true);
    setAddStudentError(null);
    try {
      const added = await api.addStudent(newStudent);
      setStudents([added, ...students]);
      setIsAddStudentOpen(false);
      setNewStudent({
        full_name: '',
        email: '',
        roll_number: '',
        program_code: 'BTECH-CSE',
        semester: 6,
        section: 'A',
        password: 'Student@123',
      });
    } catch (err: any) {
      setAddStudentError(err.message || 'Failed to enroll student');
    } finally {
      setIsAddingStudent(false);
    }
  };

  const handlePublishNoticeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noticeForm.title || !noticeForm.content) return;
    try {
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
    } catch (err: any) {
      console.error('Failed to publish notice:', err);
    }
  };

  const handleDeleteNotice = async (id: string) => {
    await api.deleteNotice(id);
    setNotices(notices.filter((n) => n.id !== id));
  };

  return (
    <div className="space-y-6">
      {/* Admin Profile & Summary Banner */}
      <div className="p-6 md:p-8 bg-white border border-slate-200 rounded-2xl shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-[#17365D] text-white flex items-center justify-center font-bold text-2xl shadow-md">
              <GraduationCap className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-slate-900">
                  Academic Management Control Panel
                </h1>
                <Badge variant="danger" size="sm">
                  Super Administrator
                </Badge>
              </div>
              <p className="text-sm text-slate-500 mt-0.5">
                Logged in as <strong className="text-slate-800">{currentUser?.full_name || 'Dean & System Admin'}</strong> • Office of Academic Affairs
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-4 py-2 rounded-xl bg-slate-50 border border-slate-200 text-right">
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Enrolled Students</span>
              <span className="text-lg font-bold text-slate-900 font-mono">{students.length} Total</span>
            </div>
            <div className="px-4 py-2 rounded-xl bg-slate-50 border border-slate-200 text-right">
              <span className="text-[10px] text-blue-700 uppercase font-mono block">Published Notices</span>
              <span className="text-lg font-bold text-blue-700 font-mono">{notices.length} Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('roster')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'roster'
              ? 'bg-[#17365D] text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Student Roster</span>
        </button>

        <button
          onClick={() => setActiveTab('notices')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'notices'
              ? 'bg-[#17365D] text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Megaphone className="w-4 h-4" />
          <span>Notice Publisher</span>
        </button>

        <button
          onClick={() => setActiveTab('assignments')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'assignments'
              ? 'bg-[#17365D] text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>Faculty Assignments</span>
        </button>
      </div>

      {/* Tab 1: Student Roster */}
      {activeTab === 'roster' && (
        <Card className="space-y-6 border border-slate-200 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Student Directory & Academic Health</h2>
              <p className="text-xs text-slate-500 mt-0.5">
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
                className="w-full pl-10 pr-4 py-2 rounded-xl input-clean text-sm placeholder:text-slate-400"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-clean rounded-xl px-3 py-2 text-sm text-slate-700 outline-none w-full sm:w-auto"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
            </select>
          </div>

          {/* Table */}
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-xs">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 text-xs uppercase font-mono">
                  <th className="py-3 px-4 font-semibold">Student & Roll No</th>
                  <th className="py-3 px-4 font-semibold">Program & Section</th>
                  <th className="py-3 px-4 font-semibold text-center">Attendance %</th>
                  <th className="py-3 px-4 font-semibold text-center">CGPA</th>
                  <th className="py-3 px-4 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredStudents.map((s) => {
                  const isLow = s.attendance_percentage < 75;
                  return (
                    <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-slate-900">{s.full_name}</div>
                        <div className="text-xs font-mono text-blue-700 font-medium">{s.roll_number}</div>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="text-slate-900">{s.program}</div>
                        <div className="text-xs text-slate-500">
                          Sem {s.semester} (Sec {s.section})
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <div className="flex items-center justify-center gap-1.5">
                          {isLow && <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />}
                          <span
                            className={`font-mono font-bold ${
                              isLow ? 'text-rose-600' : 'text-emerald-700'
                            }`}
                          >
                            {s.attendance_percentage.toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center font-mono font-semibold text-slate-800">
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
            <Card className="space-y-4 border border-slate-200 shadow-xs">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Megaphone className="w-5 h-5 text-blue-600" />
                Publish Institutional Circular
              </h3>

              {noticePublishSuccess && (
                <Alert variant="success" title="Published Successfully">
                  Notice is now visible to the student and faculty portals.
                </Alert>
              )}

              <form onSubmit={handlePublishNoticeSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Notice Title
                  </label>
                  <input
                    type="text"
                    required
                    value={noticeForm.title}
                    onChange={(e) => setNoticeForm({ ...noticeForm, title: e.target.value })}
                    placeholder="e.g. Schedule for Mid-Term Make-up Exams"
                    className="w-full input-clean rounded-xl px-3.5 py-2 text-sm text-slate-900 placeholder:text-slate-400"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Category
                    </label>
                    <select
                      value={noticeForm.category}
                      onChange={(e) =>
                        setNoticeForm({ ...noticeForm, category: e.target.value as NoticeCategory })
                      }
                      className="w-full input-clean rounded-xl px-3 py-2 text-sm text-slate-900 outline-none"
                    >
                      <option value="academic">Academic</option>
                      <option value="examination">Examination</option>
                      <option value="fees">Fees & Finance</option>
                      <option value="administrative">Administrative</option>
                      <option value="urgent">Urgent</option>
                      <option value="event">Campus Event</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
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
                      className="w-full input-clean rounded-xl px-3 py-2 text-sm text-slate-900 outline-none"
                    >
                      <option value="all">All (University-wide)</option>
                      <option value="student">Students Only</option>
                      <option value="faculty">Faculty Only</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Announcement Body
                  </label>
                  <textarea
                    rows={4}
                    required
                    value={noticeForm.content}
                    onChange={(e) => setNoticeForm({ ...noticeForm, content: e.target.value })}
                    placeholder="Type official circular content here..."
                    className="w-full input-clean rounded-xl px-3.5 py-2 text-sm text-slate-900 resize-none placeholder:text-slate-400"
                  />
                </div>

                <Button type="submit" variant="primary" className="w-full">
                  Broadcast Notice
                </Button>
              </form>
            </Card>
          </div>

          <div className="lg:col-span-7">
            <Card className="space-y-4 border border-slate-200 shadow-xs">
              <h3 className="text-lg font-bold text-slate-900">Active Notices Archive</h3>
              <div className="space-y-3">
                {notices.map((n) => (
                  <div
                    key={n.id}
                    className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-start justify-between gap-3"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="neutral" size="sm">{n.category.toUpperCase()}</Badge>
                        <span className="text-xs text-slate-500 font-mono">{n.published_at.substring(0, 10)}</span>
                      </div>
                      <h4 className="text-sm font-semibold text-slate-900">{n.title}</h4>
                      <p className="text-xs text-slate-600 line-clamp-2">{n.content}</p>
                    </div>

                    <button
                      onClick={() => handleDeleteNotice(n.id)}
                      className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
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
        <Card className="space-y-6 border border-slate-200 shadow-xs">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Faculty Course Allotments</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Active semester subject teaching assignments and student enrollments
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {facultyAssignments.map((fca) => (
              <div
                key={fca.id}
                className="p-5 rounded-xl bg-white border border-slate-200 hover:border-blue-300 hover:shadow-xs transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                      {fca.subject_code}
                    </span>
                    <Badge variant="primary" size="sm">
                      {fca.course_section}
                    </Badge>
                  </div>
                  <h4 className="text-base font-bold text-slate-900">{fca.subject_name}</h4>
                  <p className="text-sm text-slate-600 mt-1 font-medium">
                    Instructor: {fca.faculty_name}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-mono">
                  <span>Enrolled Candidates:</span>
                  <span className="font-bold text-emerald-700">{fca.enrolled_count} Students</span>
                </div>
              </div>
            ))}
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
            {addStudentError && (
              <Alert variant="danger" title="Enrollment Error">
                {addStudentError}
              </Alert>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Full Legal Name
              </label>
              <input
                type="text"
                required
                value={newStudent.full_name}
                onChange={(e) => setNewStudent({ ...newStudent, full_name: e.target.value })}
                placeholder="e.g. Vikramaditya Verma"
                className="w-full input-clean rounded-xl px-3.5 py-2 text-sm text-slate-900 placeholder:text-slate-400"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Roll Number
                </label>
                <input
                  type="text"
                  required
                  value={newStudent.roll_number}
                  onChange={(e) => setNewStudent({ ...newStudent, roll_number: e.target.value })}
                  placeholder="CS2023-0490"
                  className="w-full input-clean rounded-xl px-3.5 py-2 text-sm font-mono text-slate-900 placeholder:text-slate-400"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Section
                </label>
                <select
                  value={newStudent.section}
                  onChange={(e) => setNewStudent({ ...newStudent, section: e.target.value })}
                  className="w-full input-clean rounded-xl px-3 py-2 text-sm text-slate-900 outline-none"
                >
                  <option value="A">Section A</option>
                  <option value="B">Section B</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Program Code
                </label>
                <input
                  type="text"
                  required
                  value={newStudent.program_code}
                  onChange={(e) => setNewStudent({ ...newStudent, program_code: e.target.value })}
                  placeholder="BTECH-CSE"
                  className="w-full input-clean rounded-xl px-3.5 py-2 text-sm font-mono text-slate-900 placeholder:text-slate-400"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Semester
                </label>
                <select
                  value={newStudent.semester}
                  onChange={(e) => setNewStudent({ ...newStudent, semester: parseInt(e.target.value, 10) || 6 })}
                  className="w-full input-clean rounded-xl px-3 py-2 text-sm text-slate-900 outline-none"
                >
                  <option value={1}>Semester 1</option>
                  <option value={2}>Semester 2</option>
                  <option value={3}>Semester 3</option>
                  <option value={4}>Semester 4</option>
                  <option value={5}>Semester 5</option>
                  <option value={6}>Semester 6</option>
                  <option value={7}>Semester 7</option>
                  <option value={8}>Semester 8</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Institutional Email
              </label>
              <input
                type="email"
                required
                value={newStudent.email}
                onChange={(e) => setNewStudent({ ...newStudent, email: e.target.value })}
                placeholder="vikram.verma@csic.edu"
                className="w-full input-clean rounded-xl px-3.5 py-2 text-sm text-slate-900 placeholder:text-slate-400"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Initial Account Password
              </label>
              <input
                type="password"
                required
                value={newStudent.password}
                onChange={(e) => setNewStudent({ ...newStudent, password: e.target.value })}
                placeholder="••••••••"
                className="w-full input-clean rounded-xl px-3.5 py-2 text-sm text-slate-900 placeholder:text-slate-400"
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
              <Button type="submit" variant="primary" isLoading={isAddingStudent}>
                Confirm Enrollment
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};

export const AdminDashboard = AdminDashboardPage;
export default AdminDashboardPage;
