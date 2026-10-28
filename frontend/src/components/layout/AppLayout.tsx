import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  GraduationCap,
  MessageSquare,
  LayoutDashboard,
  CheckSquare,
  Award,
  CreditCard,
  Calendar,
  Megaphone,
  User as UserIcon,
  LogOut,
  Menu,
  X,
  Sparkles,
  Shield,
  BookOpen,
  Search,
} from 'lucide-react';

import { Profile } from '../../types';
import { Badge } from '../common/Badge';

interface AppLayoutProps {
  currentUser: Profile;
  onLogout: () => void;
  children: React.ReactNode;
}

interface NavItem {
  label: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  isPrimary?: boolean;
  badge?: string;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  currentUser,
  onLogout,
  children,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Close mobile drawer on route navigation
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Lock body scroll and handle Escape key when mobile drawer is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          setMobileMenuOpen(false);
        }
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => {
        document.body.style.overflow = '';
        window.removeEventListener('keydown', handleKeyDown);
      };
    } else {
      document.body.style.overflow = '';
    }
  }, [mobileMenuOpen]);

  const studentNavItems: NavItem[] = [
    {
      label: 'AI Chatbot',
      path: '/chat',
      icon: MessageSquare,
      isPrimary: true,
      badge: 'Primary',
    },
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: LayoutDashboard,
    },
    {
      label: 'Attendance',
      path: '/attendance',
      icon: CheckSquare,
    },
    {
      label: 'Marks & Grades',
      path: '/marks',
      icon: Award,
    },
    {
      label: 'Fee Ledger',
      path: '/fees',
      icon: CreditCard,
    },
    {
      label: 'Timetable',
      path: '/timetable',
      icon: Calendar,
    },
    {
      label: 'Notice Board',
      path: '/notices',
      icon: Megaphone,
    },
    {
      label: 'Search Info',
      path: '/search',
      icon: Search,
    },
    {
      label: 'My Profile',
      path: '/profile',
      icon: UserIcon,
    },
  ];

  const facultyNavItems: NavItem[] = [
    {
      label: 'Faculty Portal',
      path: '/faculty',
      icon: LayoutDashboard,
    },
    {
      label: 'AI Chatbot',
      path: '/chat',
      icon: MessageSquare,
      badge: 'Assistant',
    },
    {
      label: 'Notice Board',
      path: '/notices',
      icon: Megaphone,
    },
    {
      label: 'Search Info',
      path: '/search',
      icon: Search,
    },
  ];

  const adminNavItems: NavItem[] = [
    {
      label: 'Admin Portal',
      path: '/admin',
      icon: Shield,
    },
    {
      label: 'AI Chatbot',
      path: '/chat',
      icon: MessageSquare,
      badge: 'Assistant',
    },
    {
      label: 'Notice Board',
      path: '/notices',
      icon: Megaphone,
    },
    {
      label: 'Search Info',
      path: '/search',
      icon: Search,
    },
  ];


  const navItems =
    currentUser.role === 'admin'
      ? adminNavItems
      : currentUser.role === 'faculty'
      ? facultyNavItems
      : studentNavItems;

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'admin':
        return <Badge variant="danger" size="sm" icon={<Shield className="w-3 h-3" />}>ADMIN</Badge>;
      case 'faculty':
        return <Badge variant="warning" size="sm" icon={<BookOpen className="w-3 h-3" />}>FACULTY</Badge>;
      default:
        return <Badge variant="primary" size="sm" icon={<GraduationCap className="w-3 h-3" />}>STUDENT</Badge>;
    }
  };

  const getCurrentPageTitle = () => {
    const current = navItems.find((item) => item.path === location.pathname);
    if (current) return current.label;
    if (location.pathname.startsWith('/faculty')) return 'Faculty Management';
    if (location.pathname.startsWith('/admin')) return 'Administrator Console';
    if (location.pathname.startsWith('/profile')) return 'Student Profile';
    return 'Academic Portal';
  };

  return (
    <div className="min-h-screen flex bg-[#F1F4F8] text-[#101828] font-sans antialiased">
      {/* ================= DESKTOP SIDEBAR ================= */}
      <aside className="hidden lg:flex lg:flex-col w-64 bg-[#14253D] text-white shrink-0 shadow-lg z-30 select-none">
        {/* Brand Header */}
        <div className="h-16 px-5 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[#1D4ED8] flex items-center justify-center text-white shadow-md shadow-blue-950/40">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div>
              <div className="font-bold text-base tracking-tight leading-none text-white">
                CSIC Portal
              </div>
              <div className="text-[10px] text-slate-300 font-medium tracking-wide uppercase mt-1">
                Student Information
              </div>
            </div>
          </div>
        </div>

        {/* User Identity Preview in Sidebar */}
        <div className="px-5 py-4 border-b border-white/10 bg-[#0B1624]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-600/30 border border-blue-400/40 flex items-center justify-center font-bold text-white text-sm shrink-0">
              {currentUser.full_name ? currentUser.full_name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-semibold text-white truncate">
                {currentUser.full_name}
              </div>
              <div className="text-[11px] text-slate-300 font-mono truncate">
                {currentUser.roll_number || currentUser.department || currentUser.email}
              </div>
            </div>
          </div>
          <div className="mt-2.5 flex items-center justify-between">
            {getRoleBadge(currentUser.role)}
            <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Verified Active
            </span>
          </div>
        </div>

        {/* Navigation Section */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="px-3 pb-2 text-[10px] uppercase font-bold tracking-wider text-slate-400">
            Navigation Menu
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-900/30'
                    : item.isPrimary
                    ? 'bg-blue-500/15 text-blue-200 hover:bg-blue-500/25 hover:text-white border border-blue-400/20'
                    : 'text-slate-200 hover:bg-white/10 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <Icon
                    className={`w-4 h-4 shrink-0 ${
                      isActive ? 'text-white' : item.isPrimary ? 'text-blue-300' : 'text-slate-300'
                    }`}
                  />
                  <span className="truncate">{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${
                      isActive
                        ? 'bg-white text-blue-800'
                        : item.isPrimary
                        ? 'bg-blue-500 text-white'
                        : 'bg-white/20 text-slate-200'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Footer / Logout */}
        <div className="p-3 border-t border-white/10 bg-[#0E2442]/80">
          <button
            onClick={() => {
              onLogout();
              navigate('/login');
            }}
            className="w-full flex items-center gap-2.5 px-3.5 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-rose-200 hover:bg-rose-500/20 transition-colors"
          >
            <LogOut className="w-4 h-4 text-slate-400 hover:text-rose-300" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* ================= MOBILE DRAWER ================= */}
      {mobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 z-50 flex"
          role="dialog"
          aria-modal="true"
          aria-label="Navigation drawer"
        >
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm"
            onClick={() => setMobileMenuOpen(false)}
            aria-hidden="true"
          />
          <div className="relative w-72 max-w-[85%] bg-[#17365D] text-white flex flex-col h-full shadow-2xl z-10">
            <div className="h-16 px-5 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                  <GraduationCap className="w-5 h-5" />
                </div>
                <span className="font-bold text-white text-base">CSIC Portal</span>
              </div>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-white/10"
                aria-label="Close navigation menu"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* User card in mobile drawer */}
            <div className="p-4 border-b border-white/10 bg-[#0E2442]/60">
              <div className="text-sm font-semibold text-white truncate">
                {currentUser.full_name}
              </div>
              <div className="text-xs text-slate-300 font-mono truncate">
                {currentUser.roll_number || currentUser.department || currentUser.email}
              </div>
              <div className="mt-2">{getRoleBadge(currentUser.role)}</div>
            </div>

            {/* Mobile Nav Links */}
            <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;

                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium ${
                      isActive
                        ? 'bg-blue-600 text-white font-semibold'
                        : 'text-slate-200 hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="w-4 h-4 text-slate-300" />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-500 text-white font-bold">
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                );
              })}
            </nav>

            <div className="p-4 border-t border-white/10 bg-[#0E2442]">
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  onLogout();
                  navigate('/login');
                }}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm font-medium text-rose-300 hover:bg-rose-500/20 rounded-lg"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= MAIN CONTENT WRAPPER ================= */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Institutional Header */}
        <header className="sticky top-0 z-20 h-16 bg-white border-b border-slate-200 px-4 sm:px-6 lg:px-8 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              aria-label="Open mobile menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider hidden sm:inline">
                Portal
              </span>
              <span className="text-slate-300 hidden sm:inline">/</span>
              <h1 className="text-base sm:text-lg font-bold text-slate-900">
                {getCurrentPageTitle()}
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Quick Ask Chatbot button when not on /chat */}
            {location.pathname !== '/chat' && (
              <NavLink
                to="/chat"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 transition-colors shadow-xs"
              >
                <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                <span className="hidden sm:inline">Ask Academic AI</span>
                <span className="sm:hidden">Chat</span>
              </NavLink>
            )}

            {/* Student ID badge */}
            <div className="hidden md:flex items-center gap-2 pl-3 border-l border-slate-200 text-xs text-slate-600 font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>{currentUser.roll_number || currentUser.role.toUpperCase()}</span>
            </div>
          </div>
        </header>

        {/* Page Content Body */}
        <main
          className={`flex-1 min-w-0 ${
            location.pathname === '/chat'
              ? 'p-0 w-full h-[calc(100dvh-4rem)] overflow-hidden'
              : 'p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto'
          }`}
        >
          {children}
        </main>
      </div>
    </div>
  );
};
