import apiClient from './client';
import type { OnboardingJourney } from '../types';

export const onboardingApi = {
  getMyJourney: () =>
    apiClient.get<OnboardingJourney>('/onboarding/my-journey/').then(r => r.data),
  completeStep: (stepId: number) =>
    apiClient.post(`/onboarding/steps/${stepId}/complete/`).then(r => r.data),
};
