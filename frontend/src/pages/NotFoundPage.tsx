import React from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, ArrowLeft, Home } from 'lucide-react';
import { Profile } from '../types';

interface NotFoundPageProps {
  currentUser: Profile | null;
}

export const NotFoundPage: React.FC<NotFoundPageProps> = ({ currentUser }) => {
  const navigate = useNavigate();

  const handleReturn = () => {
    if (!currentUser) {
      navigate('/login');
    } else if (currentUser.role === 'admin') {
      navigate('/admin');
    } else if (currentUser.role === 'faculty') {
      navigate('/faculty');
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-[#F1F4F8] flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl border border-slate-200 shadow-xl p-8 text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 text-blue-700 flex items-center justify-center mx-auto shadow-xs">
          <GraduationCap className="w-9 h-9" />
        </div>

        <div className="space-y-2">
          <div className="inline-block px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-amber-50 text-amber-700 border border-amber-200">
            HTTP 404
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Page Not Found
          </h1>
          <p className="text-sm text-slate-600 leading-relaxed">
            The institutional resource or page you requested does not exist or may have been relocated.
          </p>
        </div>

        <div className="pt-2">
          <button
            type="button"
            onClick={handleReturn}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition-all shadow-md shadow-blue-900/10"
          >
            {currentUser ? (
              <>
                <Home className="w-4 h-4" />
                Return to Institutional Portal
              </>
            ) : (
              <>
                <ArrowLeft className="w-4 h-4" />
                Return to Login
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
