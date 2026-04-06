import apiClient from './client';
import type { LearnerDashboard, ManagerDashboard } from '../types';

export const dashboardApi = {
  getLearnerDashboard: () =>
    apiClient.get<LearnerDashboard>('/dashboard/me/').then(r => r.data),      // ← me/ pas learner/
  getManagerDashboard: () =>
    apiClient.get<ManagerDashboard>('/dashboard/manager/').then(r => r.data), // ✅ déjà correct
};