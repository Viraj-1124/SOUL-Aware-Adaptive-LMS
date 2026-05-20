import apiClient from './apiClient';

export interface GoalAlignmentRequest {
  goal_text: string;
  html_mastery: number;
  css_mastery: number;
  js_mastery: number;
  react_mastery: number;
  python_mastery: number;
  ml_mastery: number;
  dsa_mastery: number;
  environment: string;
  engagement_score: number;
  consistency_score: number;
  integrity_score: number;
  anomaly_score: number;
}

export interface GoalAlignmentResponse {
  student_id: number;
  goal_text: string;
  goal_type: string;
  goal_specificity_score: number;
  collaboration_score: number;
  alignment_score: number;
  predicted_domain: string;
  all_domain_scores: Record<string, number>;
  skill_gap: number;
  skill_gap_vector: Record<string, number>;
  weakest_topics: string[];
  context_adjustment_score: number;
  learning_mode_hint: string;
  integrity_flag: boolean;
  scaffold_level: string;
  behavior_summary: string;
  recommendation: string;
  learning_path: string[];
  resources: string[];
  explanation: string;
  confidence_score: number;
}

export interface GoalProfileOut {
  id: number;
  student_id: number;
  goal_text: string;
  goal_type: string | null;
  goal_specificity_score: number | null;
  alignment_score: number | null;
  predicted_domain: string | null;
  skill_gap: number | null;
  weakest_topics: string[] | null;
  scaffold_level: string | null;
  learning_mode_hint: string | null;
  integrity_flag: boolean | null;
  recommendation: string | null;
  learning_path: string[] | null;
  resources: string[] | null;
  confidence_score: number | null;
  behavior_summary: string | null;
  explanation: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface MasteryPrefillOut {
  html_mastery: number;
  css_mastery: number;
  js_mastery: number;
  react_mastery: number;
  python_mastery: number;
  ml_mastery: number;
  dsa_mastery: number;
  source_topics: Record<string, string[]>;
  has_data: boolean;
}

export const alignmentApi = {
  analyzeGoal: async (studentId: number, data: GoalAlignmentRequest): Promise<GoalAlignmentResponse> => {
    const response = await apiClient.post(`/alignment/analyze/${studentId}`, data);
    return response.data;
  },

  getProfile: async (studentId: number): Promise<GoalProfileOut> => {
    const response = await apiClient.get(`/alignment/profile/${studentId}`);
    return response.data;
  },

  getMasteryPrefill: async (studentId: number): Promise<MasteryPrefillOut> => {
    const response = await apiClient.get(`/alignment/mastery-prefill/${studentId}`);
    return response.data;
  },

  analyzeBatch: async (studentIds: number[]): Promise<GoalAlignmentResponse[]> => {
    const response = await apiClient.post('/alignment/analyze-batch', { student_ids: studentIds });
    return response.data;
  },

  getAllProfiles: async (): Promise<GoalProfileOut[]> => {
    const response = await apiClient.get('/alignment/all');
    return response.data;
  },
};
