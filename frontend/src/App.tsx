import React, { useState, useEffect, Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Profile, UserRole } from './types';
import { api, getStoredUser } from './services/api';
import { AppLayout } from './components/layout/AppLayout';
import { ErrorBoundary } from './components/common/ErrorBoundary';

// Route-level Code Splitting for Performance
const LoginPage = lazy(() => import('./pages/LoginPage').then((m) => ({ default: m.LoginPage })));
const StudentDashboardPage = lazy(() =>
  import('./pages/student/StudentDashboardPage').then((m) => ({ default: m.StudentDashboardPage }))
);
const ChatPage = lazy(() => import('./pages/student/ChatPage').then((m) => ({ default: m.ChatPage })));
const AttendancePage = lazy(() =>
  import('./pages/student/AttendancePage').then((m) => ({ default: m.AttendancePage }))
);
const MarksPage = lazy(() => import('./pages/student/MarksPage').then((m) => ({ default: m.MarksPage })));
const FeesPage = lazy(() => import('./pages/student/FeesPage').then((m) => ({ default: m.FeesPage })));
const TimetablePage = lazy(() =>
  import('./pages/student/TimetablePage').then((m) => ({ default: m.TimetablePage }))
);
const NoticesPage = lazy(() =>
  import('./pages/student/NoticesPage').then((m) => ({ default: m.NoticesPage }))
);
const SearchPage = lazy(() =>
  import('./pages/SearchPage').then((m) => ({ default: m.SearchPage }))
);
const ProfilePage = lazy(() =>
  import('./pages/student/ProfilePage').then((m) => ({ default: m.ProfilePage }))
);

const FacultyDashboardPage = lazy(() =>
  import('./pages/FacultyDashboardPage').then((m) => ({ default: m.FacultyDashboardPage }))
);
const AdminDashboardPage = lazy(() =>
  import('./pages/AdminDashboardPage').then((m) => ({ default: m.AdminDashboardPage }))
);
const NotFoundPage = lazy(() =>
  import('./pages/NotFoundPage').then((m) => ({ default: m.NotFoundPage }))
);

const getRoleRedirect = (role?: string) => {
  if (role === 'admin') return '/admin';
  if (role === 'faculty') return '/faculty';
  return '/dashboard';
};

const PageFallback: React.FC = () => (
  <div className="flex items-center justify-center p-12">
    <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
  </div>
);

// Resilient Protected Route Component
interface ProtectedRouteProps {
  currentUser: Profile | null;
  authLoading: boolean;
  allowedRoles?: UserRole[];
  onLogout: () => void;
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  currentUser,
  authLoading,
  allowedRoles,
  onLogout,
  children,
}) => {
  const location = useLocation();

  if (authLoading && !currentUser) {
    return (
      <div className="min-h-screen bg-[#F1F4F8] flex items-center justify-center p-4">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-xs font-mono text-slate-500 uppercase tracking-wider font-semibold">
            Restoring session...
          </p>
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(currentUser.role)) {
    return <Navigate to={getRoleRedirect(currentUser.role)} replace />;
  }

  return (
    <AppLayout currentUser={currentUser} onLogout={onLogout}>
      <Suspense fallback={<PageFallback />}>{children}</Suspense>
    </AppLayout>
  );
};

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<Profile | null>(() => getStoredUser());
  const [authLoading, setAuthLoading] = useState<boolean>(true);

  // Authenticate & validate session on initial load or refresh
  useEffect(() => {
    let isMounted = true;
    async function initSession() {
      try {
        const validatedUser = await api.validateSession();
        if (isMounted) {
          setCurrentUser(validatedUser);
        }
      } catch (err) {
        console.warn('[CSIC Auth] Session check encountered error, using local fallback:', err);
        if (isMounted) {
          setCurrentUser(getStoredUser());
        }
      } finally {
        if (isMounted) {
          setAuthLoading(false);
        }
      }
    }

    initSession();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleLoginSuccess = (user: Profile) => {
    setCurrentUser(user);
    setAuthLoading(false);
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
    setAuthLoading(false);
  };

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          {/* Public Login Route */}
          <Route
            path="/login"
            element={
              currentUser ? (
                <Navigate to={getRoleRedirect(currentUser.role)} replace />
              ) : (
                <Suspense fallback={<PageFallback />}>
                  <LoginPage onLoginSuccess={handleLoginSuccess} />
                </Suspense>
              )
            }
          />

          {/* Root Redirect */}
          <Route
            path="/"
            element={<Navigate to={currentUser ? getRoleRedirect(currentUser.role) : '/login'} replace />}
          />

          {/* AI Chatbot Assistant (Available across all authenticated roles) */}
          <Route
            path="/chat"
            element={
              <ProtectedRoute currentUser={currentUser} authLoading={authLoading} onLogout={handleLogout}>
                <ChatPage currentUser={currentUser!} />
              </ProtectedRoute>
            }
          />

          {/* Student Portal Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute
                currentUser={currentUser}
                authLoading={authLoading}
                allowedRoles={['student']}
                onLogout={handleLogout}
              >
                <StudentDashboardPage currentUser={currentUser!} />
              </ProtectedRoute>
            }
          />

          <Route
            path="/attendance"
            element={
              <ProtectedRoute
                currentUser={currentUser}
                authLoading={authLoading}
                allowedRoles={['student']}
                onLogout={handleLogout}
              >
                <AttendancePage currentUser={currentUser!} />
              </ProtectedRoute>
            }
          />

          <Route
            path="/marks"
            element={
              <ProtectedRoute
                currentUser={currentUser}
                authLoading={authLoading}
                allowedRoles={['student']}
                onLogout={handleLogout}
              >
                <MarksPage currentUser={currentUser!} />
              </ProtectedRoute>
            }
          />

          <Route
            path="/fees"
            element={
              <ProtectedRoute
                currentUser={currentUser}
                authLoading={authLoading}
                allowedRoles={['student']}
                onLogout={handleLogout}
              >
                <FeesPage currentUser={currentUser!} />
              </ProtectedRoute>
            }
          />

          <Route
            path="/timetable"
            element={
              <ProtectedRoute
                currentUser={currentUser}
                authLoading={authLoading}
                allowedRoles={['student']}
                onLogout={handleLogout}
              >
                <TimetablePage currentUser={currentUser!} />
              </ProtectedRoute>
            }
          />

          <Route
            path="/notices"
            element={
              <ProtectedRoute currentUser={currentUser} authLoading={authLoading} onLogout={handleLogout}>
                <NoticesPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/search"
            element={
              <ProtectedRoute currentUser={currentUser} authLoading={authLoading} onLogout={handleLogout}>
                <SearchPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute currentUser={currentUser} authLoading={authLoading} onLogout={handleLogout}>
                <ProfilePage currentUser={currentUser!} />
              </ProtectedRoute>
            }
          />


          {/* Faculty Dedicated Route */}
          <Route
            path="/faculty"
            element={
              <ProtectedRoute
                currentUser={currentUser}
                authLoading={authLoading}
                allowedRoles={['faculty', 'admin']}
                onLogout={handleLogout}
              >
                <FacultyDashboardPage currentUser={currentUser} />
              </ProtectedRoute>
            }
          />

          {/* Administrator Dedicated Route */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute
                currentUser={currentUser}
                authLoading={authLoading}
                allowedRoles={['admin']}
                onLogout={handleLogout}
              >
                <AdminDashboardPage currentUser={currentUser} />
              </ProtectedRoute>
            }
          />

          {/* Institutional 404 Route */}
          <Route
            path="*"
            element={
              <Suspense fallback={<PageFallback />}>
                <NotFoundPage currentUser={currentUser} />
              </Suspense>
            }
          />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
};

export default App;
