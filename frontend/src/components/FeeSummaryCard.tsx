import React, { useState } from 'react';
import { FeeInvoice } from '../types';
import { api } from '../services/api';
import { Card } from './common/Card';
import { Badge } from './common/Badge';
import { Button } from './common/Button';
import { Modal } from './common/Modal';
import { CheckCircle, FileText, ArrowUpRight, AlertCircle } from 'lucide-react';

interface FeeSummaryCardProps {
  invoices: FeeInvoice[];
  onPaymentSuccess?: () => void;
}

export const FeeSummaryCard: React.FC<FeeSummaryCardProps> = ({ invoices, onPaymentSuccess }) => {
  const [selectedInvoice, setSelectedInvoice] = useState<FeeInvoice | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [paymentSuccess, setPaymentSuccess] = useState<boolean>(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);

  const invoiceList: FeeInvoice[] = Array.isArray(invoices)
    ? invoices
    : (invoices && Array.isArray((invoices as any).invoices) ? (invoices as any).invoices : []);

  const totalAmount = invoiceList.reduce((sum, inv) => sum + (inv?.amount || 0), 0);
  const paidAmount = invoiceList.reduce(
    (sum, inv) => sum + (inv?.paid_amount !== undefined ? inv.paid_amount : (inv?.status === 'paid' ? inv?.amount || 0 : 0)),
    0
  );
  const pendingAmount = Math.max(0, totalAmount - paidAmount);


  const getStatusBadge = (status: FeeInvoice['status']) => {
    switch (status) {
      case 'paid':
        return <Badge variant="success" size="sm">PAID</Badge>;
      case 'overdue':
        return <Badge variant="danger" size="sm">OVERDUE</Badge>;
      case 'partially_paid':
        return <Badge variant="warning" size="sm">PARTIAL</Badge>;
      case 'unpaid':
      default:
        return <Badge variant="warning" size="sm">UNPAID</Badge>;
    }
  };

  const handlePayInvoice = async () => {
    if (!selectedInvoice) return;
    setIsProcessing(true);
    setPaymentError(null);
    const amountToPay = selectedInvoice.amount - (selectedInvoice.paid_amount || 0);

    try {
      await api.payInvoice(selectedInvoice.id, amountToPay > 0 ? amountToPay : selectedInvoice.amount, 'upi');
      setPaymentSuccess(true);
      if (onPaymentSuccess) {
        onPaymentSuccess();
      }
      setTimeout(() => {
        setPaymentSuccess(false);
        setIsProcessing(false);
        setSelectedInvoice(null);
      }, 1800);
    } catch (err: any) {
      setIsProcessing(false);
      setPaymentError(err.message || 'Payment settlement failed');
    }
  };

  return (
    <>
      <Card className="overflow-hidden">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div>
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              Fee Invoices & Ledger
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Semester tuition fees, laboratory amenities, and payment history
            </p>
          </div>
          <div className="text-right">
            <span className="text-xs font-mono text-slate-500 block">Outstanding Balance</span>
            <span
              className={`text-lg font-bold font-mono ${
                pendingAmount > 0 ? 'text-amber-600' : 'text-emerald-700'
              }`}
            >
              ₹{pendingAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
          </div>
        </div>

        {/* Ledger Summary KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-xs text-slate-500 block">Total Invoiced</span>
            <span className="text-base font-bold font-mono text-slate-900 mt-0.5 block">
              ₹{totalAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-xs text-emerald-700 font-medium block">Total Cleared</span>
            <span className="text-base font-bold font-mono text-emerald-700 mt-0.5 block">
              ₹{paidAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-xs text-amber-700 font-medium block">Due For Payment</span>
            <span className="text-base font-bold font-mono text-amber-700 mt-0.5 block">
              ₹{pendingAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
          </div>
        </div>

        {/* Invoice List */}
        <div className="space-y-3">
          {invoiceList.map((inv) => (
            <div
              key={inv.id}
              className="p-4 rounded-xl bg-white border border-slate-200 hover:border-slate-300 shadow-xs transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                    {inv.invoice_number}
                  </span>
                  {getStatusBadge(inv.status)}
                </div>
                <h4 className="text-sm font-semibold text-slate-900">
                  {inv.title}
                </h4>
                <div className="flex items-center gap-3 text-xs text-slate-500 font-mono">
                  <span>Due Date: {inv.due_date}</span>
                  {inv.transaction_ref && (
                    <span className="text-slate-400">Ref: {inv.transaction_ref}</span>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between sm:justify-end gap-4 border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-200">
                <div className="text-right">
                  <span className="text-sm font-bold font-mono text-slate-900 block">
                    ₹{inv.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                  <span className="text-[11px] text-slate-500 block">
                    {inv.status === 'paid' ? 'Paid in full' : 'Payable online'}
                  </span>
                </div>

                <Button
                  variant={inv.status === 'paid' ? 'secondary' : 'primary'}
                  size="sm"
                  onClick={() => setSelectedInvoice(inv)}
                  icon={inv.status === 'paid' ? <FileText className="w-3.5 h-3.5" /> : <ArrowUpRight className="w-3.5 h-3.5" />}
                >
                  {inv.status === 'paid' ? 'Receipt' : 'Pay Now'}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Invoice Details / Payment Modal */}
      {selectedInvoice && (
        <Modal
          isOpen={!!selectedInvoice}
          onClose={() => setSelectedInvoice(null)}
          title={
            selectedInvoice.status === 'paid'
              ? 'Payment Receipt & Confirmation'
              : 'Institutional Fee Settlement'
          }
        >
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Invoice Number:</span>
                <span className="font-mono text-slate-900 font-semibold">{selectedInvoice.invoice_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Description:</span>
                <span className="text-slate-900 font-medium">{selectedInvoice.title}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Total Amount:</span>
                <span className="font-mono text-slate-900 font-bold">
                  ₹{selectedInvoice.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Due Date:</span>
                <span className="font-mono text-slate-700">{selectedInvoice.due_date}</span>
              </div>
              {selectedInvoice.transaction_ref && (
                <div className="flex justify-between">
                  <span className="text-slate-500">Payment Reference:</span>
                  <span className="font-mono text-emerald-700">{selectedInvoice.transaction_ref}</span>
                </div>
              )}
            </div>

            {paymentError && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>{paymentError}</span>
              </div>
            )}

            {selectedInvoice.status !== 'paid' ? (
              <div className="space-y-3 pt-2">
                <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 space-y-1.5">
                  <div className="flex items-center gap-2 font-semibold text-xs text-amber-900">
                    <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>Demo Institutional Ledger Simulation — No real financial transaction will occur.</span>
                  </div>
                  <p className="text-[11px] text-amber-800 leading-relaxed">
                    This action will record a simulated settlement in the project's database and update your outstanding balance. No bank account, UPI app, or payment gateway is contacted.
                  </p>
                </div>

                <div className="pt-2">
                  <Button
                    variant="primary"
                    className="w-full"
                    onClick={handlePayInvoice}
                    isLoading={isProcessing}
                    disabled={isProcessing || paymentSuccess}
                  >
                    {isProcessing
                      ? 'Updating Institutional Ledger...'
                      : paymentSuccess
                      ? 'Simulated Payment Recorded!'
                      : `Confirm Simulated Payment (₹${(selectedInvoice.amount - (selectedInvoice.paid_amount || 0)).toLocaleString('en-IN')})`}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0" />
                <span className="text-xs font-medium">
                  Simulated settlement verified on the local database ledger.
                </span>
              </div>
            )}
          </div>
        </Modal>
      )}
    </>
  );
};
