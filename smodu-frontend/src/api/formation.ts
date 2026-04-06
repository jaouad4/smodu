import apiClient from './client';
import type { LearningPath, Module } from '../types';

export const formationApi = {
  getCatalog: () =>
    apiClient.get<LearningPath[]>('/formation/courses/').then(r => r.data),
  getMyEnrollments: () =>
    apiClient.get<LearningPath[]>('/formation/my-courses/').then(r => r.data),
  enroll: (courseId: string) =>
    apiClient.post('/formation/enrollments/', { course: courseId }).then(r => r.data),
  getModule: (courseId: string) =>
    apiClient.get<Module>(`/formation/courses/${courseId}/`).then(r => r.data),
  completeLesson: (lessonId: string) =>
    apiClient.post(`/formation/lessons/${lessonId}/complete/`).then(r => r.data),
};
