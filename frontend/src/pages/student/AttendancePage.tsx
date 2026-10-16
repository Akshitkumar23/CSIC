import React, { useEffect, useState } from 'react';
import { Profile, AttendanceSummary } from '../../types';
import { api } from '../../services/api';
import { AttendanceCard } from '../../components/AttendanceCard';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';

interface AttendancePageProps {
  currentUser: Profile;
}

export const AttendancePage: React.FC<AttendancePageProps> = ({ currentUser }) => {
  const [attendance, setAttendance] = useState<AttendanceSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAttendance() {
      setLoading(true);
      try {
        const data = await api.getAttendance(currentUser.id);
        setAttendance(data);
      } catch (err) {
        console.error('Failed to load attendance:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAttendance();
  }, [currentUser]);

  if (loading || !attendance) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <AttendanceCard attendance={attendance} />
    </div>
  );
};
