import React, { useState } from 'react';
import { DayOfWeek, TimetableEntry } from '../types';
import { Card } from './common/Card';
import { Clock, MapPin, User, CalendarDays } from 'lucide-react';

interface TimetableGridProps {
  schedule: TimetableEntry[];
}

const DAYS: DayOfWeek[] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

const getInitialDay = (): DayOfWeek => {
  const dayIndex = new Date().getDay(); // 0: Sun, 1: Mon, ..., 5: Fri, 6: Sat
  if (dayIndex >= 1 && dayIndex <= 5) {
    return DAYS[dayIndex - 1];
  }
  return 'Monday';
};

export const TimetableGrid: React.FC<TimetableGridProps> = ({ schedule }) => {
  const scheduleList: TimetableEntry[] = Array.isArray(schedule)
    ? (schedule.length > 0 && (schedule[0] as any).entries ? (schedule as any).flatMap((d: any) => d.entries || []) : schedule)
    : [];

  const [selectedDay, setSelectedDay] = useState<DayOfWeek>(getInitialDay);

  const dayEntries = scheduleList
    .filter((s) => s && s.day_of_week === selectedDay)
    .sort((a, b) => (a.start_time || '').localeCompare(b.start_time || ''));

  return (
    <Card className="overflow-hidden">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            Weekly Academic Timetable
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Class session schedules, lecture halls, and laboratory venues
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-xs font-mono text-slate-600 bg-slate-100 px-3 py-1.5 rounded-xl border border-slate-200">
          <CalendarDays className="w-4 h-4 text-blue-600" />
          <span>Semester VI (Section A)</span>
        </div>
      </div>

      {/* Day Selector Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-6 border-b border-slate-200 scrollbar-thin">
        {DAYS.map((day) => {
          const count = scheduleList.filter((s) => s && s.day_of_week === day).length;
          const isActive = selectedDay === day;

          return (
            <button
              key={day}
              onClick={() => setSelectedDay(day)}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:text-slate-900 hover:bg-slate-200'
              }`}
            >
              <span>{day}</span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-full font-mono ${
                  isActive ? 'bg-blue-700 text-white' : 'bg-slate-200 text-slate-700'
                }`}
              >
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Day Schedule Timeline */}
      {dayEntries.length === 0 ? (
        <div className="p-8 text-center text-slate-500 bg-slate-50 rounded-xl border border-slate-200">
          No classes scheduled for {selectedDay}. Free study / lab preparation day.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dayEntries.map((entry) => (
            <div
              key={entry.id}
              className="p-4 rounded-xl bg-white border border-slate-200 hover:border-blue-300 hover:shadow-xs transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                    {entry.subject_code}
                  </span>
                  <div className="flex items-center gap-1 text-xs text-slate-500 font-mono">
                    <Clock className="w-3.5 h-3.5 text-blue-600" />
                    <span>
                      {entry.start_time} - {entry.end_time}
                    </span>
                  </div>
                </div>

                <h4 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-2">
                  {entry.subject_name}
                </h4>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                  <span className="font-mono text-slate-700 font-medium">{entry.room_number}</span>
                </div>
                <div className="flex items-center gap-1.5 max-w-[130px] truncate">
                  <User className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span className="truncate text-slate-700">{entry.faculty_name}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
