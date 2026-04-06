import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { lazy, Suspense } from "react";
import { useAuth } from "../hooks/useAuth";
import type { UserRole } from "../types/auth";

import AuthLayout from "../layouts/AuthLayout";
import AppLayout from "../layouts/AppLayout";
import LoginPage from "../pages/auth/LoginPage";
import DashboardPage from "../pages/dashboard/DashboardPage";
import NotFoundPage from "../pages/NotFoundPage";

// Lazy load learner pages
const OnboardingPage = lazy(() => import("../pages/onboarding/OnboardingPage"));
const CatalogPage = lazy(() => import("../pages/formation/CatalogPage"));
const ModulePage = lazy(() => import("../pages/formation/ModulePage"));
const QuizPage = lazy(() => import("../pages/evaluations/QuizPage"));
const CompetencesPage = lazy(() => import("../pages/competences/CompetencesPage"));

// Fallback loader
const PageLoader = () => (
  <div className="flex h-screen items-center justify-center bg-[#f7f6f2]">
    <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#01696f] border-t-transparent" />
  </div>
);

// ── Garde : redirige vers /login si non authentifié ───────────────────
function RequireAuth({ allowedRoles }: { allowedRoles?: UserRole[] }) {
  const { isAuthenticated, isLoading, hasRole } = useAuth();

  if (isLoading) {
    return <PageLoader />;
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
        ],
      },
    ],
  },

  // ── Apprenant uniquement ────────────────────────────────────────
  {
    element: <RequireAuth allowedRoles={["LEARNER"]} />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            path: "/onboarding",
            element: (
              <Suspense fallback={<PageLoader />}>
                <OnboardingPage />
              </Suspense>
            ),
          },
          {
            path: "/evaluations/quiz/:quizId",
            element: (
              <Suspense fallback={<PageLoader />}>
                <QuizPage />
              </Suspense>
            ),
          },
        ],
      },
    ],
  },

  // ── Apprenant + Formateur ───────────────────────────────────────
  {
    element: <RequireAuth allowedRoles={["LEARNER", "TRAINER"]} />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            path: "/formation",
            element: (
              <Suspense fallback={<PageLoader />}>
                <CatalogPage />
              </Suspense>
            ),
          },
          {
            path: "/formation/modules/:moduleId",
            element: (
              <Suspense fallback={<PageLoader />}>
                <ModulePage />
              </Suspense>
            ),
          },
        ],
      },
    ],
  },

  // ── Apprenant + Manager + HR ────────────────────────────────────
  {
    element: <RequireAuth allowedRoles={["LEARNER", "MANAGER", "HR"]} />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            path: "/competences",
            element: (
              <Suspense fallback={<PageLoader />}>
                <CompetencesPage />
              </Suspense>
            ),
          },
        ],
      },
    ],
  },

  { path: "*", element: <NotFoundPage /> },
]);
