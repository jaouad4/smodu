import { axiosInstance } from './client';
import type { LearningPath, Module } from '@/types';

export const formationApi = {
  getCatalog: () =>
    axiosInstance.get<Module[]>('/formation/catalog/').then(r => r.data),

  getMyEnrollments: () =>
    axiosInstance.get<LearningPath[]>('/formation/my-enrollments/').then(r => r.data),

  enroll: (pathId: number) =>
    axiosInstance.post(`/formation/paths/${pathId}/enroll/`).then(r => r.data),

  getModule: (moduleId: number) =>
    axiosInstance.get<Module>(`/formation/modules/${moduleId}/`).then(r => r.data),

  completeLesson: (lessonId: number) =>
    axiosInstance.post(`/formation/lessons/${lessonId}/complete/`).then(r => r.data),

  getUnlockStatus: (moduleId: number) =>
    axiosInstance.get(`/formation/modules/${moduleId}/unlock-status/`).then(r => r.data),
};
