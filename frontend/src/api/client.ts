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

// Brief Extraction with Streaming - returns both content and final result
export async function* extractBriefStream(briefText: string): AsyncGenerator<{type: 'chunk' | 'final', data: any}> {
  const response = await fetch(`${API_BASE_URL}/api/extract-brief/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ brief_text: briefText }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('Failed to get response reader');
  }

  let buffer = '';
  
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          if (data.content) {
            yield { type: 'chunk', data: data.content };
          } else if (data.final) {
            yield { type: 'final', data: data.final };
            return;
          } else if (data.error) {
            throw new Error(data.error);
          } else if (data.done) {
            return;
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// Skills
export async function getSkills() {
  return fetchAPI<Skill[]>('/api/skills');
}

// Survey Generation
export async function generateSurvey(briefData: any) {
  return fetchAPI<{ survey: any; validation_log: ValidationLog }>('/api/generate-survey', {
    method: 'POST',
    body: JSON.stringify({
      brief_data: briefData,
    }),
  });
}

// Survey Generation with Streaming - returns both content and final result
export async function* generateSurveyStream(briefData: any): AsyncGenerator<{type: 'chunk' | 'final', data: any}> {
  const response = await fetch(`${API_BASE_URL}/api/generate-survey/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ brief_data: briefData }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('Failed to get response reader');
  }

  let buffer = '';
  
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          if (data.content) {
            yield { type: 'chunk', data: data.content };
          } else if (data.final) {
            yield { type: 'final', data: data.final };
            return;
          } else if (data.error) {
            throw new Error(data.error);
          } else if (data.done) {
            return;
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
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

// LOI Management
export async function updateLOI(survey: any, sliderPosition: number) {
  return fetchAPI<{ survey: any; loi_config: any }>('/api/update-loi', {
    method: 'POST',
    body: JSON.stringify({
      survey,
      slider_position: sliderPosition,
    }),
  });
}

export async function pinQuestion(survey: any, questionId: string) {
  return fetchAPI<{ survey: any; loi_config: any }>('/api/pin-question', {
    method: 'POST',
    body: JSON.stringify({
      survey,
      question_id: questionId,
    }),
  });
}

export async function excludeQuestion(survey: any, questionId: string) {
  return fetchAPI<{ survey: any; loi_config: any }>('/api/exclude-question', {
    method: 'POST',
    body: JSON.stringify({
      survey,
      question_id: questionId,
    }),
  });
}

export async function resetQuestionOverride(survey: any, questionId: string) {
  return fetchAPI<{ survey: any; loi_config: any }>('/api/reset-question-override', {
    method: 'POST',
    body: JSON.stringify({
      survey,
      question_id: questionId,
    }),
  });
}
