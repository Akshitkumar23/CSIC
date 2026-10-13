import React, { useState } from 'react';
import { DayOfWeek, TimetableEntry } from '../types';
import { Card } from './common/Card';
import { Clock, MapPin, User, CalendarDays } from 'lucide-react';

interface TimetableGridProps {
  schedule: TimetableEntry[];
}

const DAYS: DayOfWeek[] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

export const TimetableGrid: React.FC<TimetableGridProps> = ({ schedule }) => {
  const [selectedDay, setSelectedDay] = useState<DayOfWeek>('Monday');

  const dayEntries = schedule
    .filter((s) => s.day_of_week === selectedDay)
    .sort((a, b) => a.start_time.localeCompare(b.start_time));

  return (
    <Card className="overflow-hidden">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            Weekly Academic Timetable
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Class session schedules, lecture halls, and laboratory venues
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-xl border border-white/5">
          <CalendarDays className="w-4 h-4 text-indigo-400" />
          <span>Semester VI (Section A)</span>
        </div>
      </div>

      {/* Day Selector Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-6 border-b border-white/5 scrollbar-thin">
        {DAYS.map((day) => {
          const count = schedule.filter((s) => s.day_of_week === day).length;
          const isActive = selectedDay === day;

          return (
            <button
              key={day}
              onClick={() => setSelectedDay(day)}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/25 border border-indigo-400/40'
                  : 'bg-slate-800/40 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
              }`}
            >
              <span>{day}</span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-full font-mono ${
                  isActive ? 'bg-indigo-700 text-white' : 'bg-slate-700 text-slate-300'
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
        <div className="p-8 text-center text-slate-400 bg-slate-900/30 rounded-xl border border-white/5">
          No classes scheduled for {selectedDay}. Free study / lab preparation day.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dayEntries.map((entry) => (
            <div
              key={entry.id}
              className="p-4 rounded-xl bg-slate-800/50 border border-white/10 hover:border-indigo-500/30 hover:bg-slate-800/80 transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/20">
                    {entry.subject_code}
                  </span>
                  <div className="flex items-center gap-1 text-xs text-slate-400 font-mono">
                    <Clock className="w-3.5 h-3.5 text-indigo-400" />
                    <span>
                      {entry.start_time} - {entry.end_time}
                    </span>
                  </div>
                </div>

                <h4 className="text-sm font-bold text-white group-hover:text-indigo-200 transition-colors line-clamp-2">
                  {entry.subject_name}
                </h4>
              </div>

              <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs text-slate-400">
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                  <span className="font-mono text-slate-300">{entry.room_number}</span>
                </div>
                <div className="flex items-center gap-1.5 max-w-[130px] truncate">
                  <User className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span className="truncate">{entry.faculty_name}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
