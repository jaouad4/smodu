import apiClient from './client';
import type { Quiz, QuizResult, SubmitQuizPayload } from '../types';

export const evaluationsApi = {
  getQuiz: (quizId: number) =>
    apiClient.get<Quiz>(`/evaluations/quizzes/${quizId}/`).then(r => r.data),
  submitQuiz: (quizId: number, payload: SubmitQuizPayload) =>
    apiClient.post<QuizResult>(`/evaluations/quizzes/${quizId}/submit/`, payload).then(r => r.data),
  getMyAttempts: (quizId: number) =>
    apiClient.get(`/evaluations/quizzes/${quizId}/my-attempts/`).then(r => r.data),
};
