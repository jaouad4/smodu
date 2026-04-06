import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import type { UserRole } from "../types/auth";

import AuthLayout from "../layouts/AuthLayout";
import AppLayout from "../layouts/AppLayout";
import LoginPage from "../pages/auth/LoginPage";
import DashboardPage from "../pages/dashboard/DashboardPage";
import NotFoundPage from "../pages/NotFoundPage";

// ── Garde : redirige vers /login si non authentifié ───────────────────
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

  if (allowedRoles && !hasRole(...allowedRoles)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}

// ── Redirige vers /dashboard si déjà connecté ────────────────────────
function GuestOnly() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  if (isAuthenticated) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}

export const router = createBrowserRouter([
  // ── Pages publiques (non connecté seulement) ──────────────────
  {
    element: <GuestOnly />,
    children: [
      {
        element: <AuthLayout />,
        children: [
          { path: "/login", element: <LoginPage /> },
        ],
      },
    ],
  },

  // ── Pages protégées ───────────────────────────────────────────
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: "/", element: <Navigate to="/dashboard" replace /> },
          { path: "/dashboard", element: <DashboardPage /> },
          // ajoutés au fur et à mesure des steps :
          // { path: "/onboarding", element: <OnboardingPage /> },
          // { path: "/formation", element: <FormationPage /> },
          // { path: "/evaluations", element: <EvaluationsPage /> },
          // { path: "/competences", element: <CompetencesPage /> },
        ],
      },
    ],
  },

  // ── Pages manager (ADMIN, HR, MANAGER uniquement) ─────────────
  {
    element: <RequireAuth allowedRoles={["ADMIN", "HR", "MANAGER"]} />,
    children: [
      {
        element: <AppLayout />,
        children: [
          // { path: "/manager", element: <ManagerDashboardPage /> },
          // { path: "/manager/learners", element: <LearnersPage /> },
        ],
      },
    ],
  },

  { path: "*", element: <NotFoundPage /> },
]);
