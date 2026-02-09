import type { APIResponse, Project, ExtractedBrief, Skill, ValidationLog } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<APIResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    const data = await response.json();
    return data;
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

// Health Check
export async function checkHealth() {
  return fetchAPI<{ status: string; service: string; version: string }>('/api/health');
}

// Brief Extraction
export async function extractBrief(briefText: string) {
  return fetchAPI<ExtractedBrief>('/api/extract-brief', {
    method: 'POST',
    body: JSON.stringify({ brief_text: briefText }),
  });
}

// Skills
export async function getSkills() {
  return fetchAPI<Skill[]>('/api/skills');
}

// Survey Generation
export async function generateSurvey(briefData: any, selectedSkills: string[]) {
  return fetchAPI<{ survey: any; validation_log: ValidationLog }>('/api/generate-survey', {
    method: 'POST',
    body: JSON.stringify({
      brief_data: briefData,
      selected_skills: selectedSkills,
    }),
  });
}

// Survey Validation
export async function validateSurvey(surveyJson: any) {
  return fetchAPI<ValidationLog>('/api/validate-survey', {
    method: 'POST',
    body: JSON.stringify({ survey_json: surveyJson }),
  });
}

// Survey Rendering
export async function renderPreview(surveyJson: any) {
  return fetchAPI<any>('/api/render-preview', {
    method: 'POST',
    body: JSON.stringify({ survey_json: surveyJson }),
  });
}

// Project Management
export async function getProjects() {
  return fetchAPI<Project[]>('/api/projects');
}

export async function getProject(projectId: string) {
  return fetchAPI<Project>(`/api/projects/${projectId}`);
}

export async function createProject(project: Partial<Project>) {
  return fetchAPI<Project>('/api/projects', {
    method: 'POST',
    body: JSON.stringify(project),
  });
}

export async function updateProject(projectId: string, project: Partial<Project>) {
  return fetchAPI<Project>(`/api/projects/${projectId}`, {
    method: 'PUT',
    body: JSON.stringify(project),
  });
}

export async function deleteProject(projectId: string) {
  return fetchAPI<void>(`/api/projects/${projectId}`, {
    method: 'DELETE',
  });
}
