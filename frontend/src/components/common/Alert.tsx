import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react';

type AlertVariant = 'info' | 'success' | 'warning' | 'danger';

interface AlertProps {
  title?: string;
  children: React.ReactNode;
  variant?: AlertVariant;
  className?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const Alert: React.FC<AlertProps> = ({
  title,
  children,
  variant = 'info',
  className = '',
  icon,
  action,
}) => {
  const styles: Record<AlertVariant, { container: string; text: string; defaultIcon: React.ReactNode }> = {
    info: {
      container: 'bg-blue-50 border-blue-200 text-blue-900',
      text: 'text-blue-800',
      defaultIcon: <Info className="w-5 h-5 text-blue-600 shrink-0" />,
    },
    success: {
      container: 'bg-emerald-50 border-emerald-200 text-emerald-900',
      text: 'text-emerald-800',
      defaultIcon: <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0" />,
    },
    warning: {
      container: 'bg-amber-50 border-amber-200 text-amber-900',
      text: 'text-amber-800',
      defaultIcon: <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />,
    },
    danger: {
      container: 'bg-rose-50 border-rose-200 text-rose-900',
      text: 'text-rose-800',
      defaultIcon: <XCircle className="w-5 h-5 text-rose-600 shrink-0" />,
    },
  };

  const current = styles[variant];

  return (
    <div
      role="alert"
      className={twMerge(
        clsx(
          'p-4 rounded-xl border flex items-start gap-3 transition-all',
          current.container,
          className
        )
      )}
    >
      <div className="mt-0.5">{icon || current.defaultIcon}</div>
      <div className="flex-1 text-sm leading-relaxed">
        {title && <h4 className={clsx('font-semibold mb-1', current.text)}>{title}</h4>}
        <div>{children}</div>
      </div>
      {action && <div className="shrink-0 ml-2">{action}</div>}
    </div>
  );
};
