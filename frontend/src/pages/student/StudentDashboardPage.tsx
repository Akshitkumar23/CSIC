import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Profile,
  AttendanceSummary,
  Mark,
  FeeInvoice,
  TimetableEntry,
  Notice,
} from '../../types';
import { api } from '../../services/api';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';
import {
  CheckSquare,
  Award,
  CreditCard,
  Calendar,
  MessageSquare,
  Sparkles,
  ArrowRight,
  Clock,
  MapPin,
  Megaphone,
  AlertTriangle,
} from 'lucide-react';

interface StudentDashboardPageProps {
  currentUser: Profile;
}

export const StudentDashboardPage: React.FC<StudentDashboardPageProps> = ({ currentUser }) => {
  const navigate = useNavigate();
  const [attendance, setAttendance] = useState<AttendanceSummary | null>(null);
  const [marks, setMarks] = useState<Mark[]>([]);
  const [fees, setFees] = useState<FeeInvoice[]>([]);
  const [timetable, setTimetable] = useState<TimetableEntry[]>([]);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [attData, marksData, feesData, ttData, notData] = await Promise.all([
          api.getAttendance(currentUser.id),
          api.getMarks(currentUser.id),
          api.getFeeInvoices(currentUser.id),
          api.getTimetable(currentUser.id),
          api.getNotices(),
        ]);

        setAttendance(attData);
        setMarks(marksData);
        setFees(feesData);
        setTimetable(ttData);
        setNotices(notData);
      } catch (err) {
        console.error('Error fetching dashboard summary:', err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [currentUser]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  // Calculate high-level metrics
  const attendancePct = attendance?.overall_percentage ?? 0;
  const isAttendanceLow = attendancePct < 75;

  const totalFees = fees.reduce((acc, f) => acc + f.amount, 0);
  const paidFees = fees.reduce((acc, f) => acc + (f.paid_amount || 0), 0);
  const outstandingFees = Math.max(0, totalFees - paidFees);

  const totalMarks = marks.reduce((acc, m) => acc + m.marks_obtained, 0);
  const maxMarks = marks.reduce((acc, m) => acc + m.max_marks, 0);
  const avgMarks = maxMarks > 0 ? (totalMarks / maxMarks) * 100 : 0;
  const estimatedSgpa = (avgMarks / 9.5).toFixed(2);

  // Today's classes (filter for Monday by default or matching day)
  const currentDayName = 'Monday'; // Default academic day in seed data
  const todayClasses = timetable
    .filter((t) => t.day_of_week === currentDayName)
    .sort((a, b) => a.start_time.localeCompare(b.start_time));

  return (
    <div className="space-y-6">
      {/* Welcome Institutional Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-[#17365D] text-white flex items-center justify-center font-bold text-xl shadow-md shrink-0">
            {currentUser.full_name ? currentUser.full_name.charAt(0).toUpperCase() : 'S'}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900">
                Welcome, {currentUser.full_name}
              </h2>
              <Badge variant="primary" size="sm">STUDENT</Badge>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
              <span>Roll: <strong className="font-mono text-slate-700">{currentUser.roll_number || 'STU-001'}</strong></span>
              <span>•</span>
              <span>{currentUser.department || 'Computer Science & Engineering'}</span>
              <span>•</span>
              <span>Semester VI (2024-2025)</span>
            </p>
          </div>
        </div>

        <Link
          to="/chat"
          className="self-start md:self-center flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-xs transition-colors shrink-0"
        >
          <Sparkles className="w-4 h-4" />
          <span>Launch AI Chatbot</span>
        </Link>
      </div>

      {/* 4 Metric KPI Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. Attendance */}
        <Link
          to="/attendance"
          className="bg-white border border-slate-200 hover:border-blue-300 rounded-xl p-5 shadow-xs transition-all hover:shadow-sm group flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase">
                Attendance
              </span>
              <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                <CheckSquare className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span
                className={`text-2xl font-extrabold font-mono ${
                  isAttendanceLow ? 'text-rose-600' : 'text-emerald-700'
                }`}
              >
                {attendancePct.toFixed(1)}%
              </span>
              <span className="text-xs text-slate-400">/ 75% req</span>
            </div>
            {isAttendanceLow ? (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-600 mt-1.5">
                <AlertTriangle className="w-3 h-3" /> Shortage Warning
              </span>
            ) : (
              <span className="text-[11px] text-emerald-700 font-medium block mt-1.5">
                Eligible for examinations
              </span>
            )}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-blue-600 font-medium group-hover:translate-x-0.5 transition-transform">
            <span>View breakdown</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        {/* 2. Academic Result / SGPA */}
        <Link
          to="/marks"
          className="bg-white border border-slate-200 hover:border-blue-300 rounded-xl p-5 shadow-xs transition-all hover:shadow-sm group flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase">
                Estimated SGPA
              </span>
              <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
                <Award className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-extrabold font-mono text-slate-900">
                {estimatedSgpa}
              </span>
              <span className="text-xs text-slate-400">/ 10.0</span>
            </div>
            <span className="text-[11px] text-slate-500 block mt-1.5 font-medium">
              Average Score: {avgMarks.toFixed(1)}% ({marks.length} evaluations)
            </span>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-blue-600 font-medium group-hover:translate-x-0.5 transition-transform">
            <span>View marks table</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        {/* 3. Fee Ledger */}
        <Link
          to="/fees"
          className="bg-white border border-slate-200 hover:border-blue-300 rounded-xl p-5 shadow-xs transition-all hover:shadow-sm group flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase">
                Fee Dues
              </span>
              <div className="p-2 rounded-lg bg-amber-50 text-amber-600">
                <CreditCard className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span
                className={`text-2xl font-extrabold font-mono ${
                  outstandingFees > 0 ? 'text-amber-700' : 'text-emerald-700'
                }`}
              >
                ₹{outstandingFees.toLocaleString('en-IN')}
              </span>
            </div>
            <span className="text-[11px] text-slate-500 block mt-1.5 font-medium">
              {outstandingFees > 0 ? 'Pending payment balance' : 'All invoices cleared'}
            </span>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-blue-600 font-medium group-hover:translate-x-0.5 transition-transform">
            <span>View fee ledger</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        {/* 4. Today's Classes */}
        <Link
          to="/timetable"
          className="bg-white border border-slate-200 hover:border-blue-300 rounded-xl p-5 shadow-xs transition-all hover:shadow-sm group flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase">
                Today's Schedule
              </span>
              <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
                <Calendar className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-extrabold font-mono text-slate-900">
                {todayClasses.length}
              </span>
              <span className="text-xs text-slate-400">Sessions</span>
            </div>
            <span className="text-[11px] text-slate-500 block mt-1.5 font-medium">
              {todayClasses.length > 0 ? `Next: ${todayClasses[0].subject_code}` : 'No sessions today'}
            </span>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-blue-600 font-medium group-hover:translate-x-0.5 transition-transform">
            <span>View timetable</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>
      </div>

      {/* CHATBOT PROMINENT SHOWCASE BANNER */}
      <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-white border border-blue-200 rounded-2xl p-6 shadow-xs flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-2 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-blue-600 text-white">
              <Sparkles className="w-4 h-4" />
            </span>
            <h3 className="text-base sm:text-lg font-bold text-slate-900">
              Primary Product Feature: CSIC Academic AI Assistant
            </h3>
          </div>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            Need quick answers about your attendance percentage, subject grades, pending fee amounts, or official university policies? Our AI assistant directly queries your authenticated records and institutional circulars.
          </p>

          <div className="flex flex-wrap gap-2 pt-2">
            {[
              'What is my attendance percentage?',
              'Show my Mid-Term exam marks',
              'Do I have any pending fee invoices?',
              'What is my timetable today?',
            ].map((q, idx) => (
              <button
                key={idx}
                onClick={() => navigate('/chat')}
                className="text-xs bg-white hover:bg-blue-600 hover:text-white text-slate-700 font-medium px-3 py-1.5 rounded-lg border border-slate-200 hover:border-blue-600 transition-colors shadow-2xs"
              >
                "{q}"
              </button>
            ))}
          </div>
        </div>

        <Link
          to="/chat"
          className="self-start lg:self-center flex items-center gap-2 px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-sm hover:shadow transition-all shrink-0"
        >
          <MessageSquare className="w-4 h-4" />
          <span>Open Full Chatbot</span>
        </Link>
      </div>

      {/* Two Supporting Previews: Today's Classes & Recent Notices */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Today's Classes Preview */}
        <Card className="border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Clock className="w-4 h-4 text-blue-600" />
                Today's Class Schedule ({currentDayName})
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Upcoming lectures and laboratory sessions
              </p>
            </div>
            <Link
              to="/timetable"
              className="text-xs font-semibold text-blue-600 hover:text-blue-700"
            >
              Full Week →
            </Link>
          </div>

          <div className="space-y-2.5">
            {todayClasses.length === 0 ? (
              <div className="p-6 text-center text-slate-400 bg-slate-50 rounded-xl text-xs">
                No classes scheduled for today.
              </div>
            ) : (
              todayClasses.slice(0, 3).map((item) => (
                <div
                  key={item.id}
                  className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                        {item.subject_code}
                      </span>
                      <h4 className="text-sm font-semibold text-slate-900 line-clamp-1">
                        {item.subject_name}
                      </h4>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                      <span className="flex items-center gap-1 font-mono">
                        <Clock className="w-3 h-3 text-slate-400" />
                        {item.start_time} - {item.end_time}
                      </span>
                      <span className="flex items-center gap-1 font-mono">
                        <MapPin className="w-3 h-3 text-rose-500" />
                        {item.room_number}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Recent Circulars Preview */}
        <Card className="border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Megaphone className="w-4 h-4 text-blue-600" />
                Latest Notices & Circulars
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Official regulatory releases and campus updates
              </p>
            </div>
            <Link
              to="/notices"
              className="text-xs font-semibold text-blue-600 hover:text-blue-700"
            >
              All Circulars →
            </Link>
          </div>

          <div className="space-y-2.5">
            {notices.length === 0 ? (
              <div className="p-6 text-center text-slate-400 bg-slate-50 rounded-xl text-xs">
                No notices published yet.
              </div>
            ) : (
              notices.slice(0, 3).map((notice) => (
                <Link
                  key={notice.id}
                  to="/notices"
                  className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 hover:border-blue-200 block transition-colors"
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-[10px] uppercase font-bold font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                      {notice.category}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400">
                      {notice.published_at.substring(0, 10)}
                    </span>
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900 line-clamp-1">
                    {notice.title}
                  </h4>
                  <p className="text-xs text-slate-600 line-clamp-1 mt-0.5">
                    {notice.content}
                  </p>
                </Link>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
