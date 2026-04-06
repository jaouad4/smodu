import apiClient from './client';
import type { SkillMatrix } from '../types';

export const competencesApi = {
  getMyMatrix: () =>
    apiClient.get<SkillMatrix>('/competences/me/').then(r => r.data),
  getMatrices: () =>
    apiClient.get('/competences/matrices/').then(r => r.data),
  requestValidation: (skillId: string) =>
    apiClient.post(`/competences/skills/${skillId}/request-validation/`).then(r => r.data),
};
