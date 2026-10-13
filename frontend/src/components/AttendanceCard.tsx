import React, { useState } from 'react';
import { AttendanceSummary } from '../types';
import { Card } from './common/Card';
import { Alert } from './common/Alert';
import { Badge } from './common/Badge';
import { ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react';

interface AttendanceCardProps {
  attendance: AttendanceSummary;
}

export const AttendanceCard: React.FC<AttendanceCardProps> = ({ attendance }) => {
  const [expandedSubject, setExpandedSubject] = useState<string | null>(null);

  const isLow = attendance.overall_percentage < 75;
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (attendance.overall_percentage / 100) * circumference;

  const toggleSubject = (id: string) => {
    setExpandedSubject(expandedSubject === id ? null : id);
  };

  return (
    <Card className="relative overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            Attendance Analytics
            {isLow && (
              <Badge variant="danger" size="sm" icon={<AlertTriangle className="w-3 h-3" />}>
                Shortage Alert
              </Badge>
            )}
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time calculation from conducted class sessions
          </p>
        </div>
        <div className="text-right">
          <span className="text-xs font-mono text-slate-400 block">Required Threshold</span>
          <span className="text-sm font-bold text-indigo-400 font-mono">75.00%</span>
        </div>
      </div>

      {/* Low Attendance Warning Alert */}
      {isLow && (
        <div className="mb-6">
          <Alert
            variant="danger"
            title="Attendance Critical Warning (< 75%)"
            action={
              <div className="text-right">
                <span className="text-xs text-rose-300 font-mono block">Needs</span>
                <span className="text-base font-bold text-rose-200">
                  +{attendance.classes_needed_to_reach_threshold} classes
                </span>
              </div>
            }
          >
            Your current aggregate attendance of{' '}
            <strong className="text-rose-200 font-bold">{attendance.overall_percentage.toFixed(1)}%</strong>{' '}
            falls below the statutory 75% examination eligibility criteria. You must attend the next{' '}
            <strong>{attendance.classes_needed_to_reach_threshold} consecutive classes</strong> without absence to restore eligibility.
          </Alert>
        </div>
      )}

      {/* Overview Donut & Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center p-4 rounded-xl bg-slate-900/60 border border-white/5 mb-6">
        {/* SVG Circular Donut Ring */}
        <div className="md:col-span-5 flex flex-col items-center justify-center">
          <div className="relative w-36 h-36 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 128 128">
              {/* Background Circle */}
              <circle
                cx="64"
                cy="64"
                r={radius}
                className="stroke-slate-800"
                strokeWidth="11"
                fill="transparent"
              />
              {/* Progress Circle */}
              <circle
                cx="64"
                cy="64"
                r={radius}
                stroke={isLow ? '#f43f5e' : '#10b981'}
                strokeWidth="11"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span
                className={`text-2xl font-extrabold tracking-tight font-mono ${
                  isLow ? 'text-rose-400' : 'text-emerald-400'
                }`}
              >
                {attendance.overall_percentage.toFixed(1)}%
              </span>
              <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">
                Aggregate
              </span>
            </div>
          </div>
        </div>

        {/* Aggregate Numbers */}
        <div className="md:col-span-7 grid grid-cols-3 gap-3 text-center">
          <div className="p-3 rounded-xl bg-slate-800/60 border border-white/5">
            <div className="text-[11px] text-slate-400 font-medium">Conducted</div>
            <div className="text-xl font-bold text-white font-mono mt-0.5">
              {attendance.total_conducted}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Total sessions</div>
          </div>

          <div className="p-3 rounded-xl bg-slate-800/60 border border-white/5">
            <div className="text-[11px] text-emerald-400 font-medium">Attended</div>
            <div className="text-xl font-bold text-emerald-300 font-mono mt-0.5">
              {attendance.total_attended}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Present in class</div>
          </div>

          <div className="p-3 rounded-xl bg-slate-800/60 border border-white/5">
            <div className="text-[11px] text-indigo-400 font-medium">Excused</div>
            <div className="text-xl font-bold text-indigo-300 font-mono mt-0.5">
              {attendance.total_excused}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Official leave</div>
          </div>
        </div>
      </div>

      {/* Subject-Wise Breakdown List */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs font-semibold uppercase text-slate-400 px-1">
          <span>Subject Breakdown ({attendance.subjects.length})</span>
          <span>Status & Progress</span>
        </div>

        <div className="space-y-2.5">
          {attendance.subjects.map((subj) => {
            const isSubjLow = subj.percentage < 75;
            const isExpanded = expandedSubject === subj.subject_id;

            return (
              <div
                key={subj.subject_id}
                className={`p-3.5 rounded-xl border transition-all ${
                  isSubjLow
                    ? 'bg-rose-950/20 border-rose-500/30'
                    : 'bg-slate-800/40 border-white/5 hover:border-white/10'
                }`}
              >
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => toggleSubject(subj.subject_id)}
                >
                  <div className="flex-1 pr-3">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold px-1.5 py-0.5 rounded bg-slate-750 text-indigo-300 border border-white/10">
                        {subj.subject_code}
                      </span>
                      <h4 className="text-sm font-semibold text-slate-200 line-clamp-1">
                        {subj.subject_name}
                      </h4>
                    </div>
                    {subj.faculty_name && (
                      <p className="text-xs text-slate-400 mt-0.5">
                        Faculty: {subj.faculty_name}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div
                        className={`text-sm font-bold font-mono ${
                          isSubjLow ? 'text-rose-400' : 'text-emerald-400'
                        }`}
                      >
                        {subj.percentage.toFixed(1)}%
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {subj.attended_classes}/{subj.conducted_classes} classes
                      </div>
                    </div>
                    <button
                      className="p-1 rounded text-slate-400 hover:text-white transition-colors"
                      aria-label="Toggle subject details"
                    >
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-700/50 rounded-full h-1.5 mt-2.5 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isSubjLow ? 'bg-rose-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(subj.percentage, 100)}%` }}
                  />
                </div>

                {/* Expanded details */}
                {isExpanded && (
                  <div className="mt-3 pt-3 border-t border-white/5 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div className="bg-slate-900/60 p-2 rounded-lg border border-white/5">
                      <span className="text-slate-400 block text-[10px]">Conducted</span>
                      <span className="font-mono font-bold text-white">
                        {subj.conducted_classes}
                      </span>
                    </div>
                    <div className="bg-slate-900/60 p-2 rounded-lg border border-white/5">
                      <span className="text-slate-400 block text-[10px]">Attended</span>
                      <span className="font-mono font-bold text-emerald-400">
                        {subj.attended_classes}
                      </span>
                    </div>
                    <div className="bg-slate-900/60 p-2 rounded-lg border border-white/5">
                      <span className="text-slate-400 block text-[10px]">Excused</span>
                      <span className="font-mono font-bold text-indigo-400">
                        {subj.excused_classes}
                      </span>
                    </div>
                    <div className="bg-slate-900/60 p-2 rounded-lg border border-white/5">
                      <span className="text-slate-400 block text-[10px]">Classes for 75%</span>
                      <span
                        className={`font-mono font-bold ${
                          subj.classes_needed_for_75 > 0 ? 'text-rose-400' : 'text-emerald-400'
                        }`}
                      >
                        {subj.classes_needed_for_75 > 0
                          ? `+${subj.classes_needed_for_75} required`
                          : 'Satisfied'}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};
