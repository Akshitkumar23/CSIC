import React, { useEffect, useState } from 'react';
import {
  Profile,
  AttendanceWarning,
  StudentRosterItem,
  Notice,
  NoticeCategory,
} from '../types';
import { api } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Alert } from '../components/common/Alert';
import {
  GraduationCap,
  AlertTriangle,
  Users,
  Megaphone,
  Search,
  BookOpen,
  CheckCircle2,
  Send,
  Building,
  Mail,
  RefreshCw,
} from 'lucide-react';

interface FacultyDashboardProps {
  currentUser: Profile | null;
}

export const FacultyDashboard: React.FC<FacultyDashboardProps> = ({ currentUser }) => {
  const [activeTab, setActiveTab] = useState<'warnings' | 'roster' | 'notices'>('warnings');
  const [warnings, setWarnings] = useState<AttendanceWarning[]>([]);
  const [students, setStudents] = useState<StudentRosterItem[]>([]);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchRoster, setSearchRoster] = useState('');
  const [publishSuccess, setPublishSuccess] = useState(false);
  const [publishError, setPublishError] = useState<string | null>(null);

  // Notice broadcast form state
  const [noticeForm, setNoticeForm] = useState({
    title: '',
    category: 'academic' as NoticeCategory,
    target_role: 'all' as 'all' | 'student' | 'faculty',
    content: '',
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [warnData, rosterData, noticeData] = await Promise.all([
        api.getAttendanceWarnings(),
        api.getStudentRoster(),
        api.getNotices(),
      ]);
      setWarnings(warnData);
      setStudents(rosterData);
      setNotices(noticeData);
    } catch (err) {
      console.error('Failed to load faculty portal data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentUser]);

  const handlePublishNotice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noticeForm.title.trim() || !noticeForm.content.trim()) return;

    setPublishError(null);
    try {
      const published = await api.publishNotice({
        title: noticeForm.title.trim(),
        category: noticeForm.category,
        target_role: noticeForm.target_role,
        content: noticeForm.content.trim(),
      });
      setNotices([published, ...notices]);
      setNoticeForm({
        title: '',
        category: 'academic',
        target_role: 'all',
        content: '',
      });
      setPublishSuccess(true);
      setTimeout(() => setPublishSuccess(false), 3000);
    } catch (err: any) {
      setPublishError(err.message || 'Failed to broadcast announcement');
    }
  };

  const filteredStudents = students.filter(
    (s) =>
      s.full_name.toLowerCase().includes(searchRoster.toLowerCase()) ||
      s.roll_number.toLowerCase().includes(searchRoster.toLowerCase()) ||
      s.email.toLowerCase().includes(searchRoster.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* 1. Faculty Profile Header Banner */}
      <div className="p-6 md:p-8 bg-white border border-slate-200 rounded-2xl shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-[#17365D] text-white flex items-center justify-center font-bold text-2xl shadow-md">
              <GraduationCap className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-slate-900">
                  {currentUser?.full_name || 'Faculty Member'}
                </h1>
                <Badge variant="warning" size="sm">
                  FACULTY
                </Badge>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-1 font-mono">
                <span className="flex items-center gap-1">
                  <Building className="w-3.5 h-3.5 text-slate-400" />
                  {currentUser?.department || 'Computer Science & Engineering'}
                </span>
                <span className="text-slate-300">•</span>
                <span className="flex items-center gap-1">
                  <Mail className="w-3.5 h-3.5 text-slate-400" />
                  {currentUser?.email || 'faculty@csic.edu'}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center gap-3">
            <div className="px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-right">
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Enrolled Students</span>
              <span className="text-lg font-bold text-slate-900 font-mono">{students.length} Total</span>
            </div>
            <div className="px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-right">
              <span className="text-[10px] text-rose-600 uppercase font-mono block">Low Attendance Alert</span>
              <span className="text-lg font-bold text-rose-600 font-mono">{warnings.length} At-Risk</span>
            </div>
            <button
              onClick={loadData}
              title="Refresh Data"
              className="p-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 border border-slate-200 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* 2. Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('warnings')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'warnings'
              ? 'bg-rose-600 text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          <span>Attendance Warnings ({warnings.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('roster')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
            activeTab === 'roster'
              ? 'bg-[#17365D] text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Student Directory ({students.length})</span>
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
          <span>Broadcast Notice</span>
        </button>
      </div>

      {/* 3. TAB 1: Low Attendance Warnings (<75%) */}
      {activeTab === 'warnings' && (
        <Card className="space-y-6 border border-slate-200 shadow-xs">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-slate-900">Low Attendance Warning Roster</h2>
              <Badge variant="danger" size="sm">
                Threshold: &lt; 75.0%
              </Badge>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Students identified below the mandatory 75% institutional attendance threshold under Article 4.2.
            </p>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              <RefreshCw className="w-6 h-6 mx-auto animate-spin mb-2 text-blue-600" />
              Scanning attendance ledgers...
            </div>
          ) : warnings.length === 0 ? (
            <div className="p-8 rounded-xl bg-emerald-50 border border-emerald-200 text-center text-emerald-800">
              <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-emerald-600" />
              <p className="font-semibold text-sm">All Students Above Threshold</p>
              <p className="text-xs text-emerald-700 mt-1">
                Zero active low-attendance warnings detected across current courses.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {warnings.map((w) => (
                <div
                  key={w.student_id}
                  className="p-5 rounded-xl bg-rose-50/60 border border-rose-200 hover:border-rose-300 transition-all space-y-3"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-900">{w.student_name}</h3>
                      <span className="text-xs font-mono text-slate-500">Roll No: {w.roll_number}</span>
                    </div>
                    <Badge variant="danger" size="md">
                      {w.overall_percentage.toFixed(1)}%
                    </Badge>
                  </div>

                  <div>
                    <span className="text-[11px] uppercase font-mono text-slate-500 block mb-1 font-semibold">
                      Deficit Subject Modules:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {w.at_risk_subjects.map((subCode) => (
                        <span
                          key={subCode}
                          className="px-2 py-0.5 rounded bg-rose-100 border border-rose-200 text-rose-800 text-xs font-mono font-medium"
                        >
                          {subCode}
                        </span>
                      ))}
                    </div>
                  </div>

                  <p className="text-xs text-rose-700 italic pt-1 font-medium">
                    Requires immediate counseling or attendance regularization before semester end.
                  </p>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* 4. TAB 2: Student Directory */}
      {activeTab === 'roster' && (
        <Card className="space-y-6 border border-slate-200 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Enrolled Students Roster</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Inspect registered students in your department and course sections
              </p>
            </div>

            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search name or roll no..."
                value={searchRoster}
                onChange={(e) => setSearchRoster(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-xl input-clean text-xs placeholder:text-slate-400"
              />
            </div>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              <RefreshCw className="w-6 h-6 mx-auto animate-spin mb-2 text-blue-600" />
              Loading student roster...
            </div>
          ) : filteredStudents.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-sm">
              No matching student records found.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-xs">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs text-slate-600 uppercase font-mono border-b border-slate-200">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Roll Number</th>
                    <th className="py-3 px-4 font-semibold">Student Name</th>
                    <th className="py-3 px-4 font-semibold">Program & Section</th>
                    <th className="py-3 px-4 font-semibold">Email</th>
                    <th className="py-3 px-4 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredStudents.map((st) => (
                    <tr key={st.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-mono text-blue-700 font-semibold text-xs">
                        {st.roll_number}
                      </td>
                      <td className="py-3 px-4 font-medium text-slate-900">{st.full_name}</td>
                      <td className="py-3 px-4 text-xs text-slate-600">
                        {st.program} • Sec {st.section}
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-500 font-mono">{st.email}</td>
                      <td className="py-3 px-4">
                        <Badge variant="success" size="sm">
                          {st.status.toUpperCase()}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {/* 5. TAB 3: Notice Publisher */}
      {activeTab === 'notices' && (
        <Card className="space-y-6 border border-slate-200 shadow-xs">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Broadcast Campus Notice</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Publish official circulars to student cohorts or general campus channels
            </p>
          </div>

          {publishSuccess && (
            <Alert variant="success" title="Notice Published">
              The announcement has been broadcast to the official notice board.
            </Alert>
          )}

          {publishError && (
            <Alert variant="danger" title="Error">
              {publishError}
            </Alert>
          )}

          <form onSubmit={handlePublishNotice} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Announcement Title
              </label>
              <input
                type="text"
                required
                value={noticeForm.title}
                onChange={(e) => setNoticeForm({ ...noticeForm, title: e.target.value })}
                placeholder="e.g. Schedule for Cloud Architecture Guest Lecture"
                className="w-full input-clean rounded-xl px-3.5 py-2 text-sm text-slate-900 placeholder:text-slate-400"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Category
                </label>
                <select
                  value={noticeForm.category}
                  onChange={(e) => setNoticeForm({ ...noticeForm, category: e.target.value as NoticeCategory })}
                  className="w-full input-clean rounded-xl px-3 py-2 text-sm text-slate-900 outline-none"
                >
                  <option value="academic">Academic</option>
                  <option value="examination">Examination</option>
                  <option value="administrative">Administrative</option>
                  <option value="fees">Fees</option>
                  <option value="event">Event</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Target Audience
                </label>
                <select
                  value={noticeForm.target_role}
                  onChange={(e) => setNoticeForm({ ...noticeForm, target_role: e.target.value as any })}
                  className="w-full input-clean rounded-xl px-3 py-2 text-sm text-slate-900 outline-none"
                >
                  <option value="all">All Campus</option>
                  <option value="student">Students Only</option>
                  <option value="faculty">Faculty Only</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Notice Content
              </label>
              <textarea
                required
                rows={4}
                value={noticeForm.content}
                onChange={(e) => setNoticeForm({ ...noticeForm, content: e.target.value })}
                placeholder="Detail the guidelines, venue, timings, and expectations..."
                className="w-full input-clean rounded-xl px-3.5 py-2 text-sm text-slate-900 resize-none placeholder:text-slate-400"
              />
            </div>

            <div className="flex justify-end">
              <Button type="submit" variant="primary" icon={<Send className="w-4 h-4" />}>
                Broadcast Circular
              </Button>
            </div>
          </form>

          {/* Recent Notices Broadcast */}
          <div className="pt-6 border-t border-slate-200 space-y-3">
            <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-600" />
              Active Notices on Campus Board
            </h3>
            <div className="space-y-2">
              {notices.slice(0, 4).map((n) => (
                <div key={n.id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-semibold text-slate-900">{n.title}</h4>
                    <span className="text-xs text-slate-500 font-mono">
                      Category: {n.category.toUpperCase()} • Published by {n.published_by_name}
                    </span>
                  </div>
                  <Badge variant="neutral" size="sm">
                    {n.target_role.toUpperCase()}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default FacultyDashboard;
