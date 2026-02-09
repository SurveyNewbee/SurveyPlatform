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
  
  // Sample design
  total_sample_size?: number;
  quotas?: Array<{
    attribute: string;
    type: 'hard' | 'soft';
    groups: Array<{
      label: string;
      min?: number;
      max?: number;
      proportion?: number;
    }>;
  }>;
  
  // Market context
  market_context?: {
    client_brand?: string | null;
    competitor_brands?: string[];
    category?: string | null;
    market?: string | null;
  };
  
  // Study classification
  study_type?: string;
  primary_methodology?: string;
  secondary_objectives?: string[];
  
  // Operational details
  operational?: {
    target_loi_minutes?: number;
    fieldwork_mode?: string;
    market_specifics?: string;
    quality_controls?: string[];
    constraints?: string;
  };
  
  // Study design
  study_design?: any;
  
  // Measurement guidance
  measurement_guidance?: {
    measurement_priority?: string;
    required_outputs?: string[];
    segmentation_intent?: string;
    benchmarking?: string;
  };
  
  // Problem frame
  problem_frame?: {
    decision_stage?: string;
    primary_problem?: string;
    decision_risk_level?: string;
  };
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
