import React, { useEffect, useState } from 'react';
import {
  Profile,
  AttendanceSummary,
  Mark,
  FeeInvoice,
  TimetableEntry,
  Notice,
} from '../types';
import { api } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { DashboardSkeleton } from '../components/common/LoadingSkeleton';
import { AttendanceCard } from '../components/AttendanceCard';
import { MarksTable } from '../components/MarksTable';
import { TimetableGrid } from '../components/TimetableGrid';
import { FeeSummaryCard } from '../components/FeeSummaryCard';
import { NoticeBoard } from '../components/NoticeBoard';
import { ChatDrawer } from '../components/ChatDrawer';
import {
  GraduationCap,
  Building,
  CheckCircle2,
  Mail,
  Phone,
  Sparkles,
  User,
} from 'lucide-react';

interface StudentDashboardProps {
  currentUser: Profile | null;
}

export const StudentDashboard: React.FC<StudentDashboardProps> = ({ currentUser }) => {
  const [profile, setProfile] = useState<Profile | null>(currentUser);
  const [attendance, setAttendance] = useState<AttendanceSummary | null>(null);
  const [marks, setMarks] = useState<Mark[]>([]);
  const [fees, setFees] = useState<FeeInvoice[]>([]);
  const [timetable, setTimetable] = useState<TimetableEntry[]>([]);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [profData, attData, marksData, feesData, ttData, notData] = await Promise.all([
          api.getStudentProfile(currentUser?.id),
          api.getAttendance(currentUser?.id),
          api.getMarks(currentUser?.id),
          api.getFeeInvoices(currentUser?.id),
          api.getTimetable(currentUser?.id),
          api.getNotices(),
        ]);

        setProfile(profData);
        setAttendance(attData);
        setMarks(marksData);
        setFees(feesData);
        setTimetable(ttData);
        setNotices(notData);
      } catch (err) {
        console.error('Error fetching student dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [currentUser]);

  if (loading || !profile || !attendance) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <DashboardSkeleton />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* 1. Student Personal Profile Banner */}
      <Card className="p-6 md:p-8 bg-gradient-to-r from-slate-900/90 via-indigo-950/40 to-slate-900/90 border border-white/10 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="flex items-center gap-5">
            <div className="relative">
              <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-slate-800/80 border border-white/10 flex items-center justify-center text-slate-400 ring-2 ring-indigo-500/30 shadow-xl">
                <User className="w-10 h-10 text-slate-400" />
              </div>
              <span className="absolute -bottom-1 -right-1 w-5 h-5 bg-emerald-500 rounded-full ring-2 ring-slate-900 flex items-center justify-center">
                <CheckCircle2 className="w-3 h-3 text-white" />
              </span>
            </div>

            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                  {profile.full_name}
                </h1>
                <Badge variant="primary" size="sm">
                  Semester {profile.semester || 6}
                </Badge>
                <Badge variant="success" size="sm">
                  Active Enrolled
                </Badge>
              </div>

              <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs sm:text-sm text-slate-300">
                <span className="font-mono text-indigo-300 font-bold">
                  Roll No: {profile.roll_number}
                </span>
                <span className="text-slate-500">•</span>
                <span className="flex items-center gap-1 text-slate-400">
                  <GraduationCap className="w-3.5 h-3.5 text-indigo-400" />
                  {profile.program}
                </span>
                <span className="text-slate-500">•</span>
                <span className="flex items-center gap-1 text-slate-400">
                  <Building className="w-3.5 h-3.5 text-indigo-400" />
                  Section {profile.section}
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-x-4 text-xs text-slate-400 pt-1 font-mono">
                <span className="flex items-center gap-1">
                  <Mail className="w-3 h-3" />
                  {profile.email}
                </span>
                {profile.phone && (
                  <span className="flex items-center gap-1">
                    <Phone className="w-3 h-3" />
                    {profile.phone}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Quick Academic Health Pill */}
          <div className="flex sm:flex-col items-center sm:items-end justify-between border-t md:border-t-0 pt-3 md:pt-0 border-white/10">
            <span className="text-xs text-slate-400 uppercase font-mono">Department</span>
            <span className="text-sm font-semibold text-slate-200">
              {profile.department}
            </span>
            <div className="mt-2 hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>AI Chat Assistant Available</span>
            </div>
          </div>
        </div>
      </Card>

      {/* 2. Attendance Overview (With Low Attendance Warning Alert) */}
      <section aria-label="Attendance Section">
        <AttendanceCard attendance={attendance} />
      </section>

      {/* 3. Subject Marks Breakdown */}
      <section aria-label="Marks Section">
        <MarksTable marks={marks} />
      </section>

      {/* 4. Timetable & Weekly Schedule */}
      <section aria-label="Timetable Section">
        <TimetableGrid schedule={timetable} />
      </section>

      {/* 5. Invoices & Financial Ledger */}
      <section aria-label="Fee Ledger Section">
        <FeeSummaryCard invoices={fees} />
      </section>

      {/* 6. Institutional Notices */}
      <section aria-label="Notices Section">
        <NoticeBoard notices={notices} />
      </section>

      {/* 7. Floating AI Assistant Chat Drawer */}
      <ChatDrawer />
    </div>
  );
};
