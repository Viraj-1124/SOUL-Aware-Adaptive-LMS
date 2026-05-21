import apiClient from './apiClient';

export interface Alert {
  id: number;
  alert_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  message: string;
  metric_value: number | null;
  created_at: string;
  acknowledged_at: string | null;
}

export interface RemediationModule {
  id: number;
  student_id: number;
  title: string;
  description: string | null;
  skill_gap: string;
  difficulty_level: string;
  content: string;
  content_type: string;
  completion_percentage: number;
  score: number | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface ReflectionPrompt {
  id: number;
  prompt_text: string;
  context: string;
  generated_at: string;
  response: string | null;
  response_submitted_at: string | null;
  reflection_depth_score: number | null;
  sentiment: number | null;
}

export interface EthicalProfile {
  id: number;
  student_id: number;
  academic_integrity_score: number;
  collaboration_fairness_score: number;
  self_regulation_score: number;
  responsibility_index: number;
  integrity_flags: number;
  collaboration_violations: number;
  self_plagiarism_detected: boolean;
  last_violation_at: string | null;
  intervention_sent: boolean;
}

export interface EngagementSnapshot {
  id: number;
  student_id: number;
  engagement_score: number;
  activity_count: number;
  engagement_trend: string;
  timestamp: string;
}

// ============================================================================
// ALERT ENDPOINTS
// ============================================================================

export const fetchStudentAlerts = async (studentId: number, unacknowledgedOnly: boolean = false): Promise<Alert[]> => {
  try {
    const response = await apiClient.get(`/api/alerts/student/${studentId}`, {
      params: { unacknowledged_only: unacknowledgedOnly }
    });
    return response.data || [];
  } catch (error) {
    console.error('Error fetching alerts:', error);
    return [];
  }
};

export const acknowledgeAlert = async (alertId: number, acknowledgedById?: number, reason?: string): Promise<Alert | null> => {
  try {
    const response = await apiClient.post(`/api/alerts/${alertId}/acknowledge`, {
      acknowledged_by_id: acknowledgedById || 1,
      dismissal_reason: reason,
      action_taken: 'viewed'
    });
    return response.data;
  } catch (error) {
    console.error('Error acknowledging alert:', error);
    return null;
  }
};

export const checkAndCreateAlerts = async (studentId: number, courseId: number): Promise<any> => {
  try {
    const response = await apiClient.post(`/api/alerts/check/${studentId}/${courseId}`);
    return response.data;
  } catch (error) {
    console.error('Error checking alerts:', error);
    return null;
  }
};

export const createAlertRule = async (ruleData: any): Promise<any> => {
  try {
    const response = await apiClient.post('/api/alerts/rules', ruleData);
    return response.data;
  } catch (error) {
    console.error('Error creating alert rule:', error);
    return null;
  }
};

// ============================================================================
// REMEDIATION MODULE ENDPOINTS
// ============================================================================

export const fetchStudentModules = async (studentId: number, courseId: number): Promise<RemediationModule[]> => {
  try {
    const response = await apiClient.get(`/api/remediation/student/${studentId}/${courseId}`);
    return response.data || [];
  } catch (error) {
    console.error('Error fetching remediation modules:', error);
    return [];
  }
};

export const createRemediationModule = async (moduleData: any): Promise<RemediationModule | null> => {
  try {
    const response = await apiClient.post('/api/remediation/modules', moduleData);
    return response.data;
  } catch (error) {
    console.error('Error creating remediation module:', error);
    return null;
  }
};

export const updateModuleProgress = async (
  moduleId: number,
  completionPercentage: number,
  score?: number
): Promise<RemediationModule | null> => {
  try {
    const response = await apiClient.put(`/api/remediation/modules/${moduleId}`, {
      completion_percentage: completionPercentage,
      score
    });
    return response.data;
  } catch (error) {
    console.error('Error updating module progress:', error);
    return null;
  }
};

// ============================================================================
// REFLECTION PROMPT ENDPOINTS
// ============================================================================

export const fetchStudentPrompts = async (studentId: number): Promise<ReflectionPrompt[]> => {
  try {
    const response = await apiClient.get(`/api/reflection/student/${studentId}`);
    return response.data || [];
  } catch (error) {
    console.error('Error fetching reflection prompts:', error);
    return [];
  }
};

export const createReflectionPrompt = async (promptData: any): Promise<ReflectionPrompt | null> => {
  try {
    const response = await apiClient.post('/api/reflection/prompts', promptData);
    return response.data;
  } catch (error) {
    console.error('Error creating reflection prompt:', error);
    return null;
  }
};

export const submitReflection = async (promptId: number, response: string): Promise<ReflectionPrompt | null> => {
  try {
    const result = await apiClient.post(`/api/reflection/prompts/${promptId}/submit`, {
      response
    });
    return result.data;
  } catch (error) {
    console.error('Error submitting reflection:', error);
    return null;
  }
};

// ============================================================================
// ETHICS PROFILE ENDPOINTS
// ============================================================================

export const fetchEthicalProfile = async (studentId: number): Promise<EthicalProfile | null> => {
  try {
    const response = await apiClient.get(`/api/ethics/profile/${studentId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching ethical profile:', error);
    return null;
  }
};

export const flagIntegrityViolation = async (studentId: number, violation: any): Promise<any> => {
  try {
    const response = await apiClient.post(`/api/ethics/flag/${studentId}`, violation);
    return response.data;
  } catch (error) {
    console.error('Error flagging integrity violation:', error);
    return null;
  }
};

// ============================================================================
// ENGAGEMENT ENDPOINTS
// ============================================================================

export const fetchEngagementSnapshots = async (
  studentId: number,
  courseId: number,
  hours?: number
): Promise<EngagementSnapshot[]> => {
  try {
    const response = await apiClient.get(`/api/engagement/snapshots/${studentId}/${courseId}`, {
      params: { hours }
    });
    return response.data || [];
  } catch (error) {
    console.error('Error fetching engagement snapshots:', error);
    return [];
  }
};

export const createEngagementSnapshot = async (snapshotData: any): Promise<EngagementSnapshot | null> => {
  try {
    const response = await apiClient.post('/api/engagement/snapshot', snapshotData);
    return response.data;
  } catch (error) {
    console.error('Error creating engagement snapshot:', error);
    return null;
  }
};

export const fetchEngagementTrend = async (
  studentId: number,
  courseId: number,
  days?: number
): Promise<any> => {
  try {
    const response = await apiClient.get(`/api/engagement/trend/${studentId}/${courseId}`, {
      params: { days }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching engagement trend:', error);
    return null;
  }
};

// ============================================================================
// CURRICULUM ENDPOINTS
// ============================================================================

export const fetchLatestCurriculumSequence = async (
  studentId: number,
  courseId: number
): Promise<any> => {
  try {
    const response = await apiClient.get(`/api/curriculum/latest/${studentId}/${courseId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching curriculum sequence:', error);
    return null;
  }
};

export const applyCurriculumSequence = async (sequenceId: number): Promise<any> => {
  try {
    const response = await apiClient.post(`/api/curriculum/apply/${sequenceId}`);
    return response.data;
  } catch (error) {
    console.error('Error applying curriculum sequence:', error);
    return null;
  }
};

export const analyzeCurriculum = async (studentId: number, courseId: number, currentModules: number[]): Promise<any> => {
  try {
    const response = await apiClient.post(`/api/curriculum/analyze/${studentId}/${courseId}`, {
      current_modules: currentModules
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing curriculum:', error);
    return null;
  }
};
