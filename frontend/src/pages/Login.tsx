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
  const [selectedRole, setSelectedRole] = useState<UserRole>('student');
  const [email, setEmail] = useState('rashi@csic.edu');
  const [password, setPassword] = useState('1234');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleRoleChange = (role: UserRole) => {
    setSelectedRole(role);
    setErrorMessage('');
    if (role === 'student') {
      setEmail('rashi@csic.edu');
      setPassword('1234');
    } else if (role === 'faculty') {
      setEmail('rajesh.kumar@csic.edu');
      setPassword('1234');
    } else {
      setEmail('admin@csic.edu');
      setPassword('1234');
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

  const handleQuickDemoSelect = async (demoEmail: string, role: UserRole) => {
    setSelectedRole(role);
    setEmail(demoEmail);
    setPassword('1234');
    setErrorMessage('');
    setLoading(true);

    try {
      const res = await api.login(demoEmail, '1234', role);
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

          {/* Quick Demo Access Bar */}
          <div className="mt-6 pt-5 border-t border-slate-200">
            <div className="flex items-center justify-between mb-2.5">
              <span className="text-[11px] font-mono uppercase text-slate-500 font-semibold flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-amber-500" />
                Demo Accounts (Password: 1234)
              </span>
              <span className="text-[10px] text-slate-400 font-mono">1-Click Sign In</span>
            </div>

            {selectedRole === 'student' && (
              <div className="grid grid-cols-2 gap-2">
                {[
                  { name: 'Rashi', email: 'rashi@csic.edu' },
                  { name: 'Vanshika', email: 'vanshika@csic.edu' },
                  { name: 'Silki', email: 'silki@csic.edu' },
                  { name: 'Akshit', email: 'akshit@csic.edu' },
                ].map((s) => (
                  <button
                    key={s.email}
                    type="button"
                    onClick={() => handleQuickDemoSelect(s.email, 'student')}
                    className="py-1.5 px-2.5 rounded-lg bg-slate-50 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 text-xs text-slate-700 border border-slate-200 font-medium transition-all text-left flex items-center justify-between"
                  >
                    <span className="font-semibold">{s.name}</span>
                    <span className="text-[10px] text-slate-400">{s.email.split('@')[0]}</span>
                  </button>
                ))}
              </div>
            )}

            {selectedRole === 'faculty' && (
              <div className="grid grid-cols-1 gap-2">
                {[
                  { name: 'Akshit (Faculty)', email: 'rajesh.kumar@csic.edu' },
                  { name: 'Prof. Anita Deshmukh', email: 'anita.deshmukh@csic.edu' },
                ].map((f) => (
                  <button
                    key={f.email}
                    type="button"
                    onClick={() => handleQuickDemoSelect(f.email, 'faculty')}
                    className="py-1.5 px-3 rounded-lg bg-slate-50 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 text-xs text-slate-700 border border-slate-200 font-medium transition-all flex items-center justify-between"
                  >
                    <span className="font-semibold">{f.name}</span>
                    <span className="text-[10px] text-slate-400">{f.email}</span>
                  </button>
                ))}
              </div>
            )}

            {selectedRole === 'admin' && (
              <div className="grid grid-cols-1 gap-2">
                <button
                  type="button"
                  onClick={() => handleQuickDemoSelect('admin@csic.edu', 'admin')}
                  className="py-1.5 px-3 rounded-lg bg-slate-50 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 text-xs text-slate-700 border border-slate-200 font-medium transition-all flex items-center justify-between"
                >
                  <span className="font-semibold">Akshit (Admin)</span>
                  <span className="text-[10px] text-slate-400">admin@csic.edu</span>
                </button>
              </div>
            )}
          </div>
        </Card>

        {/* Institutional System Footer */}
        <div className="text-center text-xs text-slate-500 font-medium">
          Cloud-Based Student Information Chatbot (CSIC) • Academic Portal
        </div>
      </div>
    </div>
  );
};
