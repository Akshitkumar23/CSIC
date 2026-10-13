import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Profile } from './types';
import { api, getStoredUser } from './services/api';
import { Navbar } from './components/Navbar';
import { Login } from './pages/Login';
import { StudentDashboard } from './pages/StudentDashboard';
import { AdminDashboard } from './pages/AdminDashboard';

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<Profile | null>(() => {
    return getStoredUser();
  });

  const handleLoginSuccess = (user: Profile) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-navy-950 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white">
        {currentUser && (
          <Navbar
            user={currentUser}
            onLogout={handleLogout}
            unreadNoticesCount={1}
          />
        )}

        <main className="flex-1">
          <Routes>
            <Route
              path="/login"
              element={
                currentUser ? (
                  <Navigate
                    to={currentUser.role === 'admin' ? '/admin' : '/dashboard'}
                    replace
                  />
                ) : (
                  <Login onLoginSuccess={handleLoginSuccess} />
                )
              }
            />

            <Route
              path="/dashboard"
              element={
                currentUser ? (
                  <StudentDashboard currentUser={currentUser} />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />

            <Route
              path="/admin"
              element={
                currentUser ? (
                  currentUser.role === 'admin' ? (
                    <AdminDashboard currentUser={currentUser} />
                  ) : (
                    <Navigate to="/dashboard" replace />
                  )
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />

            {/* Default fallback route */}
            <Route
              path="*"
              element={
                <Navigate
                  to={
                    currentUser
                      ? currentUser.role === 'admin'
                        ? '/admin'
                        : '/dashboard'
                      : '/login'
                  }
                  replace
                />
              }
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
