import React, { useEffect, useState } from 'react';
import { Profile, Mark } from '../../types';
import { api } from '../../services/api';
import { MarksTable } from '../../components/MarksTable';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';

interface MarksPageProps {
  currentUser: Profile;
}

export const MarksPage: React.FC<MarksPageProps> = ({ currentUser }) => {
  const [marks, setMarks] = useState<Mark[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMarks() {
      setLoading(true);
      try {
        const data = await api.getMarks(currentUser.id);
        setMarks(data);
      } catch (err) {
        console.error('Failed to load marks:', err);
      } finally {
        setLoading(false);
      }
    }
    loadMarks();
  }, [currentUser]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <MarksTable marks={marks} />
    </div>
  );
};
