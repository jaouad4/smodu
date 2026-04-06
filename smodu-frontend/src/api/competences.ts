import { axiosInstance } from './client';
import type { SkillMatrix, SkillDomain } from '@/types';

export const competencesApi = {
  getMyMatrix: () =>
    axiosInstance.get<SkillMatrix>('/competences/my-matrix/').then(r => r.data),

  getDomains: () =>
    axiosInstance.get<SkillDomain[]>('/competences/domains/').then(r => r.data),
};
