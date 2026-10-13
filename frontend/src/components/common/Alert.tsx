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
      container: 'bg-indigo-950/40 border-indigo-500/30 text-indigo-200',
      text: 'text-indigo-400',
      defaultIcon: <Info className="w-5 h-5 text-indigo-400 shrink-0" />,
    },
    success: {
      container: 'bg-emerald-950/40 border-emerald-500/30 text-emerald-200',
      text: 'text-emerald-400',
      defaultIcon: <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />,
    },
    warning: {
      container: 'bg-amber-950/40 border-amber-500/40 text-amber-200',
      text: 'text-amber-400',
      defaultIcon: <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />,
    },
    danger: {
      container: 'bg-rose-950/40 border-rose-500/40 text-rose-200',
      text: 'text-rose-400',
      defaultIcon: <XCircle className="w-5 h-5 text-rose-400 shrink-0" />,
    },
  };

  const current = styles[variant];

  return (
    <div
      role="alert"
      className={twMerge(
        clsx(
          'p-4 rounded-xl border backdrop-blur-md flex items-start gap-3 transition-all',
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
