import apiClient from './client';
import type { LearningPath, Module } from '../types';

export const formationApi = {
  getCatalog: () =>
    apiClient.get<LearningPath[]>('/formation/catalog/').then(r => r.data),
  getMyEnrollments: () =>
    apiClient.get<LearningPath[]>('/formation/my-enrollments/').then(r => r.data),
  enroll: (pathId: number) =>
    apiClient.post(`/formation/paths/${pathId}/enroll/`).then(r => r.data),
  getModule: (moduleId: number) =>
    apiClient.get<Module>(`/formation/modules/${moduleId}/`).then(r => r.data),
  completeLesson: (lessonId: number) =>
    apiClient.post(`/formation/lessons/${lessonId}/complete/`).then(r => r.data),
};
