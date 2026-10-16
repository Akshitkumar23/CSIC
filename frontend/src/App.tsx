import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Profile } from './types';
import { api, getStoredUser } from './services/api';
import { AppLayout } from './components/layout/AppLayout';
import { Login } from './pages/Login';
import { StudentDashboardPage } from './pages/student/StudentDashboardPage';
import { ChatPage } from './pages/student/ChatPage';
import { AttendancePage } from './pages/student/AttendancePage';
import { MarksPage } from './pages/student/MarksPage';
import { FeesPage } from './pages/student/FeesPage';
import { TimetablePage } from './pages/student/TimetablePage';
import { NoticesPage } from './pages/student/NoticesPage';
import { ProfilePage } from './pages/student/ProfilePage';
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
      <Routes>
        {/* Public Login Route */}
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

        {/* Authenticated Application Routes (Wrapped in AppLayout) */}
        {currentUser ? (
          <>
            {/* Primary AI Chatbot Assistant (Available to all roles) */}
            <Route
              path="/chat"
              element={
                <AppLayout currentUser={currentUser} onLogout={handleLogout}>
                  <ChatPage currentUser={currentUser} />
                </AppLayout>
              }
            />

            {/* Student Dedicated Multi-Page Routes */}
            <Route
              path="/dashboard"
              element={
                currentUser.role === 'faculty' ? (
                  <Navigate to="/faculty" replace />
                ) : currentUser.role === 'admin' ? (
                  <Navigate to="/admin" replace />
                ) : (
                  <AppLayout currentUser={currentUser} onLogout={handleLogout}>
                    <StudentDashboardPage currentUser={currentUser} />
                  </AppLayout>
                )
              }
            />

            <Route
              path="/attendance"
              element={
                currentUser.role === 'student' ? (
                  <AppLayout currentUser={currentUser} onLogout={handleLogout}>
                    <AttendancePage currentUser={currentUser} />
                  </AppLayout>
                ) : (
                  <Navigate to={getRoleRedirect(currentUser.role)} replace />
                )
              }
            />

            <Route
              path="/marks"
              element={
                currentUser.role === 'student' ? (
                  <AppLayout currentUser={currentUser} onLogout={handleLogout}>
                    <MarksPage currentUser={currentUser} />
                  </AppLayout>
                ) : (
                  <Navigate to={getRoleRedirect(currentUser.role)} replace />
                )
              }
            />

            <Route
              path="/fees"
              element={
                currentUser.role === 'student' ? (
                  <AppLayout currentUser={currentUser} onLogout={handleLogout}>
                    <FeesPage currentUser={currentUser} />
                  </AppLayout>
                ) : (
                  <Navigate to={getRoleRedirect(currentUser.role)} replace />
                )
              }
            />

            <Route
              path="/timetable"
              element={
                currentUser.role === 'student' ? (
                  <AppLayout currentUser={currentUser} onLogout={handleLogout}>
                    <TimetablePage currentUser={currentUser} />
                  </AppLayout>
                ) : (
                  <Navigate to={getRoleRedirect(currentUser.role)} replace />
                )
              }
            />

            <Route
              path="/notices"
              element={
                <AppLayout currentUser={currentUser} onLogout={handleLogout}>
                  <NoticesPage />
                </AppLayout>
              }
            />

            <Route
              path="/profile"
              element={
                <AppLayout currentUser={currentUser} onLogout={handleLogout}>
                  <ProfilePage currentUser={currentUser} />
                </AppLayout>
              }
            />

            {/* Faculty Dedicated Route */}
            <Route
              path="/faculty"
              element={
                currentUser.role === 'faculty' || currentUser.role === 'admin' ? (
                  <AppLayout currentUser={currentUser} onLogout={handleLogout}>
                    <FacultyDashboard currentUser={currentUser} />
                  </AppLayout>
                ) : (
                  <Navigate to="/dashboard" replace />
                )
              }
            />

            {/* Admin Dedicated Route */}
            <Route
              path="/admin"
              element={
                currentUser.role === 'admin' ? (
                  <AppLayout currentUser={currentUser} onLogout={handleLogout}>
                    <AdminDashboard currentUser={currentUser} />
                  </AppLayout>
                ) : (
                  <Navigate to={getRoleRedirect(currentUser.role)} replace />
                )
              }
            />
          </>
        ) : null}

        {/* Catch-all Fallback */}
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
    </BrowserRouter>
  );
};

export default App;
