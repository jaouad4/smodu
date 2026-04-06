import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { onboardingApi } from '@/api/onboarding';

export const useMyJourney = () =>
  useQuery({
    queryKey: ['onboarding', 'journey'],
    queryFn: onboardingApi.getMyJourney,
  });

export const useCompleteStep = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: onboardingApi.completeStep,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['onboarding', 'journey'] }),
  });
};
