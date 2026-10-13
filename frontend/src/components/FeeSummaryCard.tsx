import React, { useState } from 'react';
import { FeeInvoice } from '../types';
import { Card } from './common/Card';
import { Badge } from './common/Badge';
import { Button } from './common/Button';
import { Modal } from './common/Modal';
import { CreditCard, CheckCircle, FileText, ArrowUpRight } from 'lucide-react';

interface FeeSummaryCardProps {
  invoices: FeeInvoice[];
}

export const FeeSummaryCard: React.FC<FeeSummaryCardProps> = ({ invoices }) => {
  const [selectedInvoice, setSelectedInvoice] = useState<FeeInvoice | null>(null);
  const [paymentSuccess, setPaymentSuccess] = useState<boolean>(false);

  const totalAmount = invoices.reduce((sum, inv) => sum + inv.amount, 0);
  const paidAmount = invoices.reduce((sum, inv) => sum + (inv.paid_amount || 0), 0);
  const pendingAmount = totalAmount - paidAmount;

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

  const handleSimulatePayment = () => {
    setPaymentSuccess(true);
    setTimeout(() => {
      setPaymentSuccess(false);
      setSelectedInvoice(null);
    }, 1800);
  };

  return (
    <>
      <Card className="overflow-hidden">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              Fee Invoices & Ledger
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Semester tuition fees, laboratory amenities, and payment history
            </p>
          </div>
          <div className="text-right">
            <span className="text-xs font-mono text-slate-400 block">Outstanding Balance</span>
            <span
              className={`text-lg font-bold font-mono ${
                pendingAmount > 0 ? 'text-amber-400' : 'text-emerald-400'
              }`}
            >
              ₹{pendingAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
          </div>
        </div>

        {/* Ledger Summary KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5">
            <span className="text-xs text-slate-400 block">Total Invoiced</span>
            <span className="text-base font-bold font-mono text-white mt-0.5 block">
              ₹{totalAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5">
            <span className="text-xs text-emerald-400 block">Total Cleared</span>
            <span className="text-base font-bold font-mono text-emerald-300 mt-0.5 block">
              ₹{paidAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5">
            <span className="text-xs text-amber-400 block">Due For Payment</span>
            <span className="text-base font-bold font-mono text-amber-300 mt-0.5 block">
              ₹{pendingAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
          </div>
        </div>

        {/* Invoice List */}
        <div className="space-y-3">
          {invoices.map((inv) => (
            <div
              key={inv.id}
              className="p-4 rounded-xl bg-slate-800/40 border border-white/5 hover:border-white/10 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-white/5">
                    {inv.invoice_number}
                  </span>
                  {getStatusBadge(inv.status)}
                </div>
                <h4 className="text-sm font-semibold text-slate-200">
                  {inv.title}
                </h4>
                <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
                  <span>Due Date: {inv.due_date}</span>
                  {inv.transaction_ref && (
                    <span className="text-slate-500">Ref: {inv.transaction_ref}</span>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between sm:justify-end gap-4 border-t sm:border-t-0 pt-2 sm:pt-0 border-white/5">
                <div className="text-right">
                  <span className="text-sm font-bold font-mono text-white block">
                    ₹{inv.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                  <span className="text-[11px] text-slate-400 block">
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
            <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Invoice Number:</span>
                <span className="font-mono text-white">{selectedInvoice.invoice_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Description:</span>
                <span className="text-white font-medium">{selectedInvoice.title}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Total Amount:</span>
                <span className="font-mono text-white font-bold">
                  ₹{selectedInvoice.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Due Date:</span>
                <span className="font-mono text-slate-300">{selectedInvoice.due_date}</span>
              </div>
              {selectedInvoice.transaction_ref && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Payment Reference:</span>
                  <span className="font-mono text-emerald-400">{selectedInvoice.transaction_ref}</span>
                </div>
              )}
            </div>

            {selectedInvoice.status !== 'paid' ? (
              <div className="space-y-3 pt-2">
                <p className="text-xs text-slate-400">
                  Select payment gateway: UPI (Google Pay, PhonePe), Net Banking, or Institutional Debit Card.
                </p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-3 rounded-lg border border-indigo-500/30 bg-indigo-500/10 text-indigo-200 flex items-center gap-2 cursor-pointer">
                    <CreditCard className="w-4 h-4 text-indigo-400" />
                    <span>UPI / Instant QR</span>
                  </div>
                  <div className="p-3 rounded-lg border border-white/10 bg-slate-800/60 text-slate-300 flex items-center gap-2 cursor-pointer">
                    <FileText className="w-4 h-4 text-slate-400" />
                    <span>Net Banking / RTGS</span>
                  </div>
                </div>

                <div className="pt-3">
                  <Button
                    variant="primary"
                    className="w-full"
                    onClick={handleSimulatePayment}
                    isLoading={paymentSuccess}
                  >
                    {paymentSuccess ? 'Processing Gateway...' : `Authorize ₹${selectedInvoice.amount.toLocaleString('en-IN')}`}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
                <span className="text-xs">
                  Transaction verified on the official ledger. Downloaded receipts are valid for semester registration.
                </span>
              </div>
            )}
          </div>
        </Modal>
      )}
    </>
  );
};
