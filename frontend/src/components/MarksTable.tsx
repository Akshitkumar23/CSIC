import React, { useState, useMemo } from 'react';
import { Mark } from '../types';
import { Card } from './common/Card';
import { Badge } from './common/Badge';
import { Search, Award, TrendingUp, Filter } from 'lucide-react';

interface MarksTableProps {
  marks: Mark[];
}

export const MarksTable: React.FC<MarksTableProps> = ({ marks }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedExam, setSelectedExam] = useState<string>('all');

  const examTypes = useMemo(() => {
    const set = new Set<string>();
    marks.forEach((m) => set.add(m.exam_name));
    return ['all', ...Array.from(set)];
  }, [marks]);

  const filteredMarks = useMemo(() => {
    return marks.filter((m) => {
      const matchExam = selectedExam === 'all' || m.exam_name === selectedExam;
      const matchSearch =
        m.subject_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.subject_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.grade.toLowerCase().includes(searchQuery.toLowerCase());
      return matchExam && matchSearch;
    });
  }, [marks, searchQuery, selectedExam]);

  // Aggregate metrics
  const stats = useMemo(() => {
    if (!marks.length) return { average: 0, totalMarks: 0, maxMarks: 0 };
    const totalMarks = marks.reduce((acc, m) => acc + m.marks_obtained, 0);
    const maxMarks = marks.reduce((acc, m) => acc + m.max_marks, 0);
    const average = maxMarks > 0 ? (totalMarks / maxMarks) * 100 : 0;
    return { average, totalMarks, maxMarks };
  }, [marks]);

  const getGradeVariant = (grade: string) => {
    if (grade.startsWith('A')) return 'success';
    if (grade.startsWith('B')) return 'primary';
    if (grade.startsWith('C')) return 'warning';
    return 'danger';
  };

  return (
    <Card className="overflow-hidden">
      {/* Header and Aggregate Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            Academic Performance & Marks
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Verified evaluations and continuous assessment breakdown
          </p>
        </div>

        {/* Aggregate KPI */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-slate-900/60 border border-white/5">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-mono block">
                Average Score
              </span>
              <span className="text-base font-bold text-white font-mono">
                {stats.average.toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-slate-900/60 border border-white/5">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-mono block">
                Estimated SGPA
              </span>
              <span className="text-base font-bold text-emerald-400 font-mono">
                {(stats.average / 9.5).toFixed(2)} / 10
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by subject code, title or grade..."
            className="w-full pl-10 pr-4 py-2 rounded-xl glass-input text-sm placeholder:text-slate-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <select
            value={selectedExam}
            onChange={(e) => setSelectedExam(e.target.value)}
            className="glass-input rounded-xl px-3 py-2 text-sm text-slate-200 outline-none"
          >
            {examTypes.map((t) => (
              <option key={t} value={t} className="bg-slate-900 text-slate-200">
                {t === 'all' ? 'All Evaluations' : t}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Responsive Table */}
      <div className="overflow-x-auto rounded-xl border border-white/5 bg-slate-900/30">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="border-b border-white/10 bg-slate-800/40 text-slate-400 text-xs uppercase font-mono">
              <th className="py-3 px-4 font-semibold">Subject & Code</th>
              <th className="py-3 px-4 font-semibold">Evaluation Type</th>
              <th className="py-3 px-4 font-semibold">Exam Date</th>
              <th className="py-3 px-4 font-semibold text-right">Score</th>
              <th className="py-3 px-4 font-semibold text-center">Grade</th>
              <th className="py-3 px-4 font-semibold">Performance</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {filteredMarks.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-400">
                  No evaluation records matching criteria.
                </td>
              </tr>
            ) : (
              filteredMarks.map((mark) => (
                <tr
                  key={mark.id}
                  className="hover:bg-slate-800/30 transition-colors"
                >
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2.5">
                      <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                        {mark.subject_code}
                      </span>
                      <span className="font-medium text-slate-200">
                        {mark.subject_name}
                      </span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300 text-xs">
                    {mark.exam_name}
                  </td>
                  <td className="py-3.5 px-4 text-slate-400 text-xs font-mono">
                    {mark.exam_date}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <span className="font-mono font-bold text-white">
                      {mark.marks_obtained}
                    </span>
                    <span className="text-slate-500 font-mono text-xs">
                      /{mark.max_marks}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <Badge variant={getGradeVariant(mark.grade)} size="sm">
                      {mark.grade}
                    </Badge>
                  </td>
                  <td className="py-3.5 px-4 w-44">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-700/50 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            mark.percentage >= 85
                              ? 'bg-emerald-500'
                              : mark.percentage >= 70
                              ? 'bg-indigo-500'
                              : 'bg-amber-500'
                          }`}
                          style={{ width: `${mark.percentage}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono text-slate-300 w-10 text-right">
                        {mark.percentage.toFixed(0)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
