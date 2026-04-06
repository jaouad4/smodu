import { axiosInstance } from './client';
import type { OnboardingJourney } from '@/types';

export const onboardingApi = {
  getMyJourney: () =>
    axiosInstance.get<OnboardingJourney>('/onboarding/my-journey/').then(r => r.data),

  completeStep: (stepId: number) =>
    axiosInstance.post(`/onboarding/steps/${stepId}/complete/`).then(r => r.data),
};
