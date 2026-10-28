import React, { useEffect, useState } from 'react';
import { Profile, TimetableEntry } from '../../types';
import { api } from '../../services/api';
import { TimetableGrid } from '../../components/TimetableGrid';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface TimetablePageProps {
  currentUser: Profile;
}

export const TimetablePage: React.FC<TimetablePageProps> = ({ currentUser }) => {
  const endpoint = `/api/v1/timetable/student/${currentUser.id}`;
  const initialCached = api.getCachedData<TimetableEntry[]>(endpoint, currentUser.id);

  const [schedule, setSchedule] = useState<TimetableEntry[]>(() => initialCached || []);
  const [loading, setLoading] = useState<boolean>(() => !initialCached);
  const [error, setError] = useState<string | null>(null);

  const loadTimetable = async (forceFresh = false) => {
    if (schedule.length === 0) {
      setLoading(true);
    }
    setError(null);
    try {
      const data = await api.getTimetable(currentUser.id, { skipCache: forceFresh });
      setSchedule(data);
    } catch (err: any) {
      console.error('Failed to load timetable:', err);
      if (schedule.length === 0) {
        setError(err.message || 'Unable to retrieve academic schedule.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTimetable();
  }, [currentUser.id]);

  if (loading && schedule.length === 0) {
    return <DashboardSkeleton />;
  }

  if (error && schedule.length === 0) {
    return (
      <div className="max-w-md mx-auto my-12 p-8 bg-white border border-slate-200 rounded-2xl shadow-xs text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-800">Timetable Unavailable</h3>
        <p className="text-sm text-slate-600">
          {error || 'Unable to retrieve your weekly lecture schedule from the server.'}
        </p>
        <button
          type="button"
          onClick={() => loadTimetable(true)}
          className="inline-flex items-center justify-center gap-2 py-2 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-all shadow-sm"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <TimetableGrid schedule={schedule} />
    </div>
  );
};
