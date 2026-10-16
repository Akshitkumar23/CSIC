import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface SkeletonProps {
  className?: string;
  count?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '', count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className={twMerge(
            clsx(
              'animate-pulse bg-slate-200/80 rounded-lg',
              className
            )
          )}
        />
      ))}
    </>
  );
};

export const DashboardSkeleton: React.FC = () => {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-28 bg-slate-200/80 rounded-2xl border border-slate-200" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="h-64 bg-slate-200/80 rounded-2xl border border-slate-200" />
        <div className="h-64 bg-slate-200/80 rounded-2xl border border-slate-200" />
        <div className="h-64 bg-slate-200/80 rounded-2xl border border-slate-200" />
      </div>
      <div className="h-96 bg-slate-200/80 rounded-2xl border border-slate-200" />
    </div>
  );
};
