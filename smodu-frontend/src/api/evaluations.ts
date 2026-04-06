import { axiosInstance } from './client';
import type { Quiz, QuizAttempt, SubmitAnswerPayload } from '@/types';

export const evaluationsApi = {
  getQuiz: (quizId: number) =>
    axiosInstance.get<Quiz>(`/evaluations/quizzes/${quizId}/`).then(r => r.data),

  submitQuiz: (quizId: number, answers: SubmitAnswerPayload[]) =>
    axiosInstance.post(`/evaluations/quizzes/${quizId}/submit/`, { answers }).then(r => r.data),

  getMyAttempts: () =>
    axiosInstance.get<QuizAttempt[]>('/evaluations/my-attempts/').then(r => r.data),

  getResults: (quizId: number) =>
    axiosInstance.get(`/evaluations/quizzes/${quizId}/results/`).then(r => r.data),
};
