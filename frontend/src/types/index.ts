// Base API types matching backend models

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  brief_text?: string;
  brief_data?: any;
  survey_json?: any;
  validation_log?: any;
  rendered_preview?: any;
  created_at: string;
  updated_at: string;
}

export interface ExtractedBrief {
  objectives: string[];
  target_audience: string;
  topics: string[];
  budget?: string;
  timeline?: string;
  identified_skills: string[];
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  category?: string;
}

export interface ValidationLogEntry {
  rule_id: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  location?: string;
}

export interface ValidationLog {
  is_valid: boolean;
  error_count: number;
  warning_count: number;
  entries: ValidationLogEntry[];
}
