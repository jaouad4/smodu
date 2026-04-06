import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import type { UserRole } from '../types/auth';

import AuthLayout from '../layouts/AuthLayout';
import AppLayout from '../layouts/AppLayout';
import LoginPage from '../pages/auth/LoginPage';
import DashboardPage from '../pages/dashboard/DashboardPage';
import OnboardingPage from '../pages/onboarding/OnboardingPage';
import CatalogPage from '../pages/formation/CatalogPage';
import ModulePage from '../pages/formation/ModulePage';
import QuizPage from '../pages/evaluations/QuizPage';
import CompetencesPage from '../pages/competences/CompetencesPage';
import NotFoundPage from '../pages/NotFoundPage';

function RequireAuth({ allowedRoles }: { allowedRoles?: UserRole[] }) {
  const { isAuthenticated, isLoading, hasRole } = useAuth();
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#f7f6f2]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#01696f] border-t-transparent" />
      </div>
    );
  }
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (allowedRoles && !hasRole(...allowedRoles)) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}

function GuestOnly() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  if (isAuthenticated) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}

export const router = createBrowserRouter([
  {
    element: <GuestOnly />,
    children: [
      { element: <AuthLayout />, children: [{ path: '/login', element: <LoginPage /> }] },
    ],
  },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: '/',            element: <Navigate to="/dashboard" replace /> },
          { path: '/dashboard',   element: <DashboardPage /> },
          { path: '/onboarding',  element: <OnboardingPage /> },
          { path: '/formation',   element: <CatalogPage /> },
          { path: '/formation/modules/:moduleId', element: <ModulePage /> },
          { path: '/evaluations/quiz/:quizId',    element: <QuizPage /> },
          { path: '/competences', element: <CompetencesPage /> },
        ],
      },
    ],
  },
  {
    element: <RequireAuth allowedRoles={['ADMIN', 'HR', 'MANAGER']} />,
    children: [
      {
        element: <AppLayout />,
        children: [
          // Step 14 : ManagerDashboard, LearnersPage
        ],
      },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
]);

