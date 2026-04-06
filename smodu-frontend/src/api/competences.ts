import apiClient from './client';
import type { SkillMatrix } from '../types';

export const competencesApi = {
  getMyMatrix: () =>
    apiClient.get<SkillMatrix>('/competences/me/').then(r => r.data),
  getMatrices: () =>
    apiClient.get('/competences/matrices/').then(r => r.data),
};
