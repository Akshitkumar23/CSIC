import React, { useEffect, useState } from 'react';
import { Profile, FeeInvoice } from '../../types';
import { api } from '../../services/api';
import { FeeSummaryCard } from '../../components/FeeSummaryCard';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';

interface FeesPageProps {
  currentUser: Profile;
}

export const FeesPage: React.FC<FeesPageProps> = ({ currentUser }) => {
  const [fees, setFees] = useState<FeeInvoice[]>([]);
  const [loading, setLoading] = useState(true);

  const loadFees = async () => {
    try {
      const data = await api.getFeeInvoices(currentUser.id);
      setFees(data);
    } catch (err) {
      console.error('Failed to load fee invoices:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFees();
  }, [currentUser]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <FeeSummaryCard invoices={fees} onPaymentSuccess={loadFees} />
    </div>
  );
};
