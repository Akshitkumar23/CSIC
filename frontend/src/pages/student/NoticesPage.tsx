import React, { useEffect, useState } from 'react';
import { Notice } from '../../types';
import { api } from '../../services/api';
import { NoticeBoard } from '../../components/NoticeBoard';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export const NoticesPage: React.FC = () => {
  const [notices, setNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadNotices = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getNotices();
      setNotices(data);
    } catch (err: any) {
      console.error('Failed to load notices:', err);
      setError(err.message || 'Unable to retrieve university notices.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotices();
  }, []);

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error && notices.length === 0) {
    return (
      <div className="max-w-md mx-auto my-12 p-8 bg-white border border-slate-200 rounded-2xl shadow-xs text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-800">Notice Board Unavailable</h3>
        <p className="text-sm text-slate-600">
          {error || 'Unable to retrieve campus circulars from the server.'}
        </p>
        <button
          type="button"
          onClick={loadNotices}
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
      <NoticeBoard notices={notices} />
    </div>
  );
};
