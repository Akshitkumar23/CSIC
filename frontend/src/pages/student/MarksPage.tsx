import React, { useEffect, useState } from 'react';
import { Profile, Mark } from '../../types';
import { api } from '../../services/api';
import { MarksTable } from '../../components/MarksTable';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface MarksPageProps {
  currentUser: Profile;
}

export const MarksPage: React.FC<MarksPageProps> = ({ currentUser }) => {
  const endpoint = `/api/v1/marks/student/${currentUser.id}`;
  const initialCached = api.getCachedData<Mark[]>(endpoint, currentUser.id);

  const [marks, setMarks] = useState<Mark[]>(() => initialCached || []);
  const [loading, setLoading] = useState<boolean>(() => !initialCached);
  const [error, setError] = useState<string | null>(null);

  const loadMarks = async (forceFresh = false) => {
    if (marks.length === 0) {
      setLoading(true);
    }
    setError(null);
    try {
      const data = await api.getMarks(currentUser.id, { skipCache: forceFresh });
      setMarks(data);
    } catch (err: any) {
      console.error('Failed to load marks:', err);
      if (marks.length === 0) {
        setError(err.message || 'Unable to retrieve academic marks.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMarks();
  }, [currentUser.id]);

  if (loading && marks.length === 0) {
    return <DashboardSkeleton />;
  }

  if (error && marks.length === 0) {
    return (
      <div className="max-w-md mx-auto my-12 p-8 bg-white border border-slate-200 rounded-2xl shadow-xs text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-800">Marks Unavailable</h3>
        <p className="text-sm text-slate-600">
          {error || 'Unable to retrieve your examination results from the server.'}
        </p>
        <button
          type="button"
          onClick={() => loadMarks(true)}
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
      <MarksTable marks={marks} />
    </div>
  );
};
