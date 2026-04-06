import apiClient from './client';

export interface LearnerSummary {
  user: { id: string; full_name: string; email: string; department: string };
  completion_percentage: number;
  quiz_avg_score: number;
  project_status: string;
}

export interface LearnerDetail {
  user: { id: string; full_name: string; email: string; role: string; department: string; date_joined: string };
  onboarding: { id: string; template_title: string; progress_percentage: number; is_completed: boolean }[];
  courses: { id: string; course_title: string; difficulty: string; progress_percentage: number; completed_at: string | null }[];
  recent_quiz_attempts: { quiz_title: string; score: number | null; is_passed: boolean; submitted_at: string }[];
  competences: { total: number; validated: number; validation_rate: number };
  competences_by_category: Record<string, {
    total: number; validated: number;
    items: { name: string; level: number; required: number; is_validated: boolean }[];
  }>;
}

export interface PendingValidation {
  id: string;
  user: { id: string; full_name: string; email: string; department: string };
  competence: { id: string; name: string; category: string };
  current_level: number;
  requested_level: number;
  requested_at: string;
}

export const usersApi = {
  getLearners: () =>
    apiClient.get('/dashboard/manager/').then(r => r.data.learners as LearnerSummary[]),
  getLearnerDetail: (id: string) =>
    apiClient.get<LearnerDetail>(`/dashboard/learner-report/${id}/`).then(r => r.data),
  getUsers: () =>
    apiClient.get<any[]>('/users/').then(r => r.data),
  updateUserRole: (id: string, role: string) =>
    apiClient.patch(`/users/${id}/`, { role }).then(r => r.data),
  deactivateUser: (id: string) =>
    apiClient.patch(`/users/${id}/`, { is_active: false }).then(r => r.data),
  getPendingValidations: () =>
    apiClient.get<PendingValidation[]>('/competences/pending-validations/').then(r => r.data),
  validateCompetence: (id: string, level: number) =>
    apiClient.post(`/competences/validate/${id}/`, { level }).then(r => r.data),
  rejectValidation: (id: string) =>
    apiClient.post(`/competences/reject/${id}/`).then(r => r.data),
};