import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { GraduationCap, LogOut, Bell, Shield, BookOpen } from 'lucide-react';
import { Profile } from '../types';
import { Badge } from './common/Badge';

interface NavbarProps {
  user: Profile | null;
  onLogout: () => void;
  unreadNoticesCount?: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  user,
  onLogout,
  unreadNoticesCount = 0,
}) => {
  const navigate = useNavigate();

  const getRoleBadgeVariant = (role?: string) => {
    switch (role) {
      case 'admin':
        return 'danger';
      case 'faculty':
        return 'warning';
      case 'student':
      default:
        return 'primary';
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-white/10 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <Link
            to={user?.role === 'admin' ? '/admin' : '/dashboard'}
            className="flex items-center gap-2.5 group transition-transform active:scale-95"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25 border border-indigo-400/30 group-hover:scale-105 transition-all">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-indigo-100 to-indigo-300 bg-clip-text text-transparent">
                  CSIC
                </span>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  Cloud Portal
                </span>
              </div>
              <span className="text-[11px] text-slate-400 font-medium block -mt-1 hidden sm:block">
                Student Information & Academic Intelligence
              </span>
            </div>
          </Link>
        </div>

        {/* Navigation & Controls */}
        <div className="flex items-center gap-3 sm:gap-4">
          {user && (
            <>
              {/* Role pill */}
              <div className="hidden sm:flex items-center">
                <Badge
                  variant={getRoleBadgeVariant(user.role)}
                  size="md"
                  icon={user.role === 'admin' ? <Shield className="w-3.5 h-3.5" /> : <BookOpen className="w-3.5 h-3.5" />}
                >
                  {user.role.toUpperCase()}
                </Badge>
              </div>

              {/* Notification icon */}
              <div className="relative">
                <button
                  aria-label="View notifications"
                  onClick={() => {
                    const noticeEl = document.getElementById('notices-section');
                    if (noticeEl) {
                      noticeEl.scrollIntoView({ behavior: 'smooth' });
                    }
                  }}
                  className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors relative"
                >
                  <Bell className="w-5 h-5" />
                  {unreadNoticesCount > 0 && (
                    <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-rose-500 rounded-full ring-2 ring-slate-900 animate-pulse" />
                  )}
                </button>
              </div>

              {/* User preview */}
              <div className="flex items-center gap-3 pl-2 sm:pl-3 border-l border-white/10">
                <div className="w-9 h-9 rounded-full ring-2 ring-indigo-500/40 overflow-hidden bg-slate-800 shrink-0 flex items-center justify-center font-bold text-sm text-indigo-300">
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="hidden md:block text-left">
                  <div className="text-sm font-semibold text-slate-200 truncate max-w-[140px]">
                    {user.full_name}
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono">
                    {user.roll_number || user.department || user.role}
                  </div>
                </div>

                {/* Logout */}
                <button
                  onClick={() => {
                    onLogout();
                    navigate('/login');
                  }}
                  title="Sign Out"
                  aria-label="Sign Out"
                  className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors ml-1"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
