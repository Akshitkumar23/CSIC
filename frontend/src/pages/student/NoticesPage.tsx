import React, { useEffect, useState } from 'react';
import { Notice } from '../../types';
import { api } from '../../services/api';
import { NoticeBoard } from '../../components/NoticeBoard';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';

export const NoticesPage: React.FC = () => {
  const [notices, setNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadNotices() {
      setLoading(true);
      try {
        const data = await api.getNotices();
        setNotices(data);
      } catch (err) {
        console.error('Failed to load notices:', err);
      } finally {
        setLoading(false);
      }
    }
    loadNotices();
  }, []);

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <NoticeBoard notices={notices} />
    </div>
  );
};
