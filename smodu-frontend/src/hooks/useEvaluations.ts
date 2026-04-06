import { useQuery, useMutation } from '@tanstack/react-query';
import { evaluationsApi } from '@/api/evaluations';
import type { SubmitAnswerPayload } from '@/types';

export const useQuiz = (quizId: number) =>
  useQuery({
    queryKey: ['quiz', quizId],
    queryFn: () => evaluationsApi.getQuiz(quizId),
    enabled: !!quizId,
  });

export const useSubmitQuiz = (quizId: number) =>
  useMutation({
    mutationFn: (answers: SubmitAnswerPayload[]) =>
      evaluationsApi.submitQuiz(quizId, answers),
  });

export const useQuizResults = (quizId: number) =>
  useQuery({
    queryKey: ['quiz', quizId, 'results'],
    queryFn: () => evaluationsApi.getResults(quizId),
    enabled: !!quizId,
  });
