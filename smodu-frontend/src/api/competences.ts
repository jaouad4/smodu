import apiClient from './client';
import type { SkillMatrix } from '../types';

export const competencesApi = {
  getMyMatrix: () =>
    apiClient.get<SkillMatrix>('/competences/my-matrix/').then(r => r.data),
  requestValidation: (skillId: number) =>
    apiClient.post(`/competences/skills/${skillId}/request-validation/`).then(r => r.data),
};
