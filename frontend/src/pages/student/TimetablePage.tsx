import React, { useEffect, useState } from 'react';
import { Profile, TimetableEntry } from '../../types';
import { api } from '../../services/api';
import { TimetableGrid } from '../../components/TimetableGrid';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';

interface TimetablePageProps {
  currentUser: Profile;
}

export const TimetablePage: React.FC<TimetablePageProps> = ({ currentUser }) => {
  const [schedule, setSchedule] = useState<TimetableEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTimetable() {
      setLoading(true);
      try {
        const data = await api.getTimetable(currentUser.id);
        setSchedule(data);
      } catch (err) {
        console.error('Failed to load timetable:', err);
      } finally {
        setLoading(false);
      }
    }
    loadTimetable();
  }, [currentUser]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <TimetableGrid schedule={schedule} />
    </div>
  );
};
