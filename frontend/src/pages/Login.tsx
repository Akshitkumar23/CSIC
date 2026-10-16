import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserRole, Profile } from '../types';
import { api } from '../services/api';
import {
  GraduationCap,
  Shield,
  BookOpen,
  ArrowRight,
  Lock,
  Mail,
  Zap,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';

interface LoginProps {
  onLoginSuccess: (user: Profile) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const navigate = useNavigate();
  const isProduction = import.meta.env.PROD;
  const [selectedRole, setSelectedRole] = useState<UserRole>('student');
  const [email, setEmail] = useState(isProduction ? '' : 'aarav.sharma@csic.edu');
  const [password, setPassword] = useState(isProduction ? '' : 'Student@123');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleRoleChange = (role: UserRole) => {
    setSelectedRole(role);
    setErrorMessage('');
    if (!isProduction) {
      if (role === 'student') {
        setEmail('aarav.sharma@csic.edu');
        setPassword('Student@123');
      } else if (role === 'faculty') {
        setEmail('rajesh.kumar@csic.edu');
        setPassword('Faculty@123');
      } else {
        setEmail('admin@csic.edu');
        setPassword('Admin@123');
      }
    } else {
      setEmail('');
      setPassword('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');

    try {
      const res = await api.login(email, password, selectedRole);
      onLoginSuccess(res.user);
      if (res.user.role === 'admin') {
        navigate('/admin');
      } else if (res.user.role === 'faculty') {
        navigate('/faculty');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemoLogin = async (role: UserRole) => {
    if (isProduction) {
      setErrorMessage('Instant demo login is strictly disabled in production mode for institutional security.');
      return;
    }
    setSelectedRole(role);
    setLoading(true);
    let demoEmail = 'aarav.sharma@csic.edu';
    let demoPassword = 'Student@123';
    if (role === 'faculty') {
      demoEmail = 'rajesh.kumar@csic.edu';
      demoPassword = 'Faculty@123';
    }
    if (role === 'admin') {
      demoEmail = 'admin@csic.edu';
      demoPassword = 'Admin@123';
    }

    try {
      const res = await api.login(demoEmail, demoPassword, role);
      onLoginSuccess(res.user);
      if (res.user.role === 'admin') {
        navigate('/admin');
      } else if (res.user.role === 'faculty') {
        navigate('/faculty');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Quick login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-2xl bg-[#17365D] text-white shadow-md shadow-blue-950/20 mb-2">
            <GraduationCap className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
            CSIC Portal
          </h1>
          <p className="text-sm text-slate-500 max-w-xs mx-auto">
            Cloud-Based Student Information Chatbot & Academic Management System
          </p>
        </div>

        {/* Main Login Card */}
        <Card className="p-8 border-slate-200 shadow-md bg-white rounded-2xl">
          {/* Role Switcher Tabs */}
          <div className="grid grid-cols-3 gap-1.5 p-1 rounded-xl bg-slate-100 border border-slate-200 mb-6">
            <button
              type="button"
              onClick={() => handleRoleChange('student')}
              className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                selectedRole === 'student'
                  ? 'bg-[#17365D] text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Student</span>
            </button>
            <button
              type="button"
              onClick={() => handleRoleChange('faculty')}
              className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                selectedRole === 'faculty'
                  ? 'bg-[#17365D] text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <GraduationCap className="w-3.5 h-3.5" />
              <span>Faculty</span>
            </button>
            <button
              type="button"
              onClick={() => handleRoleChange('admin')}
              className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                selectedRole === 'admin'
                  ? 'bg-[#17365D] text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Shield className="w-3.5 h-3.5" />
              <span>Admin</span>
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {errorMessage && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
                {errorMessage}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-700">
                Institutional Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl input-clean text-sm placeholder:text-slate-400"
                  placeholder="name@university.edu"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-700">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl input-clean text-sm placeholder:text-slate-400"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full py-2.5 mt-2"
              isLoading={loading}
              icon={<ArrowRight className="w-4 h-4" />}
            >
              Sign In as {selectedRole.toUpperCase()}
            </Button>
          </form>

          {/* Quick Demo Access Bar (Development only) */}
          {!isProduction && (
            <div className="mt-6 pt-6 border-t border-slate-200">
              <span className="text-[11px] font-mono uppercase text-slate-500 block mb-2.5 text-center flex items-center justify-center gap-1.5 font-semibold">
                <Zap className="w-3.5 h-3.5 text-amber-500" />
                1-Click Instant Demo Login (Dev Mode)
              </span>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => handleQuickDemoLogin('student')}
                  className="py-1.5 px-2 rounded-lg bg-slate-50 hover:bg-slate-100 text-xs text-slate-700 border border-slate-200 font-medium transition-all"
                >
                  Student Demo
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickDemoLogin('faculty')}
                  className="py-1.5 px-2 rounded-lg bg-slate-50 hover:bg-slate-100 text-xs text-slate-700 border border-slate-200 font-medium transition-all"
                >
                  Faculty Demo
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickDemoLogin('admin')}
                  className="py-1.5 px-2 rounded-lg bg-slate-50 hover:bg-slate-100 text-xs text-slate-700 border border-slate-200 font-medium transition-all"
                >
                  Admin Demo
                </button>
              </div>
            </div>
          )}
        </Card>

        {/* Institutional System Footer */}
        <div className="text-center text-xs text-slate-500 font-medium">
          Cloud-Based Student Information Chatbot (CSIC) • Academic Portal
        </div>
      </div>
    </div>
  );
};
