import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Profile } from './types';
import { api, getStoredUser } from './services/api';
import { Navbar } from './components/Navbar';
import { Login } from './pages/Login';
import { StudentDashboard } from './pages/StudentDashboard';
import { FacultyDashboard } from './pages/FacultyDashboard';
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

  const getRoleRedirect = (role?: string) => {
    if (role === 'admin') return '/admin';
    if (role === 'faculty') return '/faculty';
    return '/dashboard';
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
                  <Navigate to={getRoleRedirect(currentUser.role)} replace />
                ) : (
                  <Login onLoginSuccess={handleLoginSuccess} />
                )
              }
            />

            <Route
              path="/dashboard"
              element={
                !currentUser ? (
                  <Navigate to="/login" replace />
                ) : currentUser.role === 'faculty' ? (
                  <Navigate to="/faculty" replace />
                ) : currentUser.role === 'admin' ? (
                  <Navigate to="/admin" replace />
                ) : (
                  <StudentDashboard currentUser={currentUser} />
                )
              }
            />

            <Route
              path="/faculty"
              element={
                !currentUser ? (
                  <Navigate to="/login" replace />
                ) : currentUser.role === 'student' ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <FacultyDashboard currentUser={currentUser} />
                )
              }
            />

            <Route
              path="/admin"
              element={
                !currentUser ? (
                  <Navigate to="/login" replace />
                ) : currentUser.role !== 'admin' ? (
                  <Navigate to={getRoleRedirect(currentUser.role)} replace />
                ) : (
                  <AdminDashboard currentUser={currentUser} />
                )
              }
            />

            {/* Default fallback route */}
            <Route
              path="*"
              element={
                <Navigate
                  to={currentUser ? getRoleRedirect(currentUser.role) : '/login'}
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
