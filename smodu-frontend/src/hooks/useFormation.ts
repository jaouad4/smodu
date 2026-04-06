import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { formationApi } from '@/api/formation';

export const useCatalog = () =>
  useQuery({ queryKey: ['formation', 'catalog'], queryFn: formationApi.getCatalog });

export const useMyEnrollments = () =>
  useQuery({ queryKey: ['formation', 'enrollments'], queryFn: formationApi.getMyEnrollments });

export const useModule = (moduleId: number) =>
  useQuery({
    queryKey: ['formation', 'module', moduleId],
    queryFn: () => formationApi.getModule(moduleId.toString()),
    enabled: !!moduleId,
  });

export const useCompleteLesson = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: formationApi.completeLesson,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['formation'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};
