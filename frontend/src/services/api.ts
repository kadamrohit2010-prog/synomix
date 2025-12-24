import axios from 'axios';
import type {
  Experiment,
  AnalysisResults,
  GEODataset,
  Team,
  UserSettings,
  ChatMessage,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Experiments
export const createExperiment = async (name: string, cancer_type: string): Promise<Experiment> => {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('cancer_type', cancer_type);
  const response = await api.post('/api/experiment/create', formData);
  return response.data;
};

export const getExperiments = async (): Promise<Experiment[]> => {
  const response = await api.get('/api/experiments');
  return response.data;
};

export const getExperiment = async (id: string): Promise<Experiment> => {
  const response = await api.get(`/api/experiment/${id}`);
  return response.data;
};

export const shareExperiment = async (id: string): Promise<{ share_url: string }> => {
  const response = await api.post(`/api/experiment/${id}/share`);
  return response.data;
};

// File Upload
export const uploadFile = async (
  experimentId: string,
  file: File,
  layerType?: string,
  onProgress?: (progress: number) => void
): Promise<{ layer_type: string; gene_count: number; sample_count: number }> => {
  const formData = new FormData();
  formData.append('file', file);
  if (layerType) {
    formData.append('layer_type', layerType);
  }

  const response = await api.post(`/api/experiment/${experimentId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });
  return response.data;
};

// Analysis
export const analyzeExperiment = async (experimentId: string): Promise<AnalysisResults> => {
  const response = await api.post(`/api/experiment/${experimentId}/analyze`);
  return response.data;
};

export const batchAnalyze = async (experimentIds: string[]): Promise<AnalysisResults[]> => {
  const response = await api.post('/api/experiments/batch-analyze', { experiment_ids: experimentIds });
  return response.data;
};

export const survivalAnalysis = async (
  experimentId: string,
  survivalData: Array<{ sample_id: string; time: number; event: boolean }>
): Promise<any> => {
  const response = await api.post(`/api/experiment/${experimentId}/survival`, { survival_data: survivalData });
  return response.data;
};

// GEO Integration
export const searchGEO = async (query: string, organism?: string): Promise<GEODataset[]> => {
  const response = await api.get('/api/geo/search', {
    params: { query, organism },
  });
  return response.data;
};

export const importGEO = async (accession: string, experimentId: string): Promise<void> => {
  await api.post(`/api/geo/import/${accession}`, { experiment_id: experimentId });
};

// cBioPortal Integration
export const searchCBioPortal = async (cancerType: string): Promise<any[]> => {
  const response = await api.get('/api/cbioportal/studies', {
    params: { cancer_type: cancerType },
  });
  return response.data;
};

export const importCBioPortal = async (studyId: string, experimentId: string): Promise<void> => {
  await api.post(`/api/cbioportal/import/${studyId}`, { experiment_id: experimentId });
};

// AI Chat
export const chatWithAI = async (
  experimentId: string,
  message: string,
  history: ChatMessage[]
): Promise<string> => {
  const response = await api.post('/api/chat', {
    experiment_id: experimentId,
    message,
    history,
  });
  return response.data.response;
};

// Teams & Collaboration
export const createTeam = async (name: string, description: string): Promise<Team> => {
  const response = await api.post('/api/teams', { name, description });
  return response.data;
};

export const getTeams = async (): Promise<Team[]> => {
  const response = await api.get('/api/teams');
  return response.data;
};

export const addTeamMember = async (teamId: string, email: string, role: string): Promise<void> => {
  await api.post(`/api/teams/${teamId}/members`, { email, role });
};

export const shareWithTeam = async (experimentId: string, teamId: string): Promise<void> => {
  await api.post(`/api/experiment/${experimentId}/share-team`, { team_id: teamId });
};

// Export
export const exportPDF = async (experimentId: string): Promise<Blob> => {
  const response = await api.get(`/api/experiment/${experimentId}/export/pdf`, {
    responseType: 'blob',
  });
  return response.data;
};

export const exportFigure = async (
  experimentId: string,
  figureType: string,
  format: 'png' | 'svg' | 'pdf'
): Promise<Blob> => {
  const response = await api.get(`/api/experiment/${experimentId}/export/figure`, {
    params: { figure_type: figureType, format },
    responseType: 'blob',
  });
  return response.data;
};

// Settings
export const getUserSettings = async (): Promise<UserSettings> => {
  const response = await api.get('/api/settings');
  return response.data;
};

export const updateUserSettings = async (settings: Partial<UserSettings>): Promise<UserSettings> => {
  const response = await api.put('/api/settings', settings);
  return response.data;
};

export default api;
