import { useQuery, useMutation } from '@tanstack/react-query';
import { evaluationsApi } from '../api/evaluations';
import type { SubmitQuizPayload } from '../types';

export const useQuiz = (quizId: string) =>
  useQuery({
    queryKey: ['quiz', quizId],
    queryFn: () => evaluationsApi.getQuiz(quizId),
    enabled: !!quizId,
  });

export const useStartQuiz = (quizId: string) =>
  useMutation({
    mutationFn: () => evaluationsApi.startQuiz(quizId),
  });

export const useSubmitQuiz = (attemptId: string) =>
  useMutation({
    mutationFn: (payload: SubmitQuizPayload) =>
      evaluationsApi.submitQuiz(attemptId, payload),
  });

export const useMyAttempts = () =>
  useQuery({
    queryKey: ['quiz', 'attempts'],
    queryFn: evaluationsApi.getMyAttempts,
  });