import apiClient from './client';
import type { Quiz, QuizResult, SubmitQuizPayload } from '../types';

export const evaluationsApi = {
  getQuiz: (quizId: string) =>
    apiClient.get<Quiz>(`/evaluations/quizzes/${quizId}/`).then(r => r.data),
  startQuiz: (quizId: string) =>
    apiClient.post<{ attempt_id: string }>(`/evaluations/quizzes/${quizId}/start/`).then(r => r.data),
  submitQuiz: (attemptId: string, payload: SubmitQuizPayload) =>
    apiClient.post<QuizResult>(`/evaluations/attempts/${attemptId}/submit/`, payload).then(r => r.data),
  getMyAttempts: () =>
    apiClient.get(`/evaluations/my-attempts/`).then(r => r.data),
};
