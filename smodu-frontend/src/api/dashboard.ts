import apiClient from './client';
import type { LearnerDashboard, ManagerDashboard } from '../types';

export const dashboardApi = {
  getLearnerDashboard: () =>
    apiClient.get<LearnerDashboard>('/dashboard/learner/').then(r => r.data),
  getManagerDashboard: () =>
    apiClient.get<ManagerDashboard>('/dashboard/manager/').then(r => r.data),
};
