import React, { useEffect, useState } from 'react';
import { Profile, FeeInvoice } from '../../types';
import { api } from '../../services/api';
import { FeeSummaryCard } from '../../components/FeeSummaryCard';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface FeesPageProps {
  currentUser: Profile;
}

export const FeesPage: React.FC<FeesPageProps> = ({ currentUser }) => {
  const [fees, setFees] = useState<FeeInvoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadFees = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getFeeInvoices(currentUser.id);
      setFees(data);
    } catch (err: any) {
      console.error('Failed to load fee invoices:', err);
      setError(err.message || 'Unable to retrieve fee records.');
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

  if (error && fees.length === 0) {
    return (
      <div className="max-w-md mx-auto my-12 p-8 bg-white border border-slate-200 rounded-2xl shadow-xs text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-800">Fee Ledger Unavailable</h3>
        <p className="text-sm text-slate-600">
          {error || 'Unable to retrieve your fee invoices from the server.'}
        </p>
        <button
          type="button"
          onClick={loadFees}
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
      <FeeSummaryCard invoices={fees} onPaymentSuccess={loadFees} />
    </div>
  );
};
