export type SourceType = 'AUDIO' | 'WHATSAPP' | 'SMS' | 'SOCIAL_MEDIA' | 'MANUAL' | 'FILE';
export type EmergencyType = 'Flood' | 'Fire' | 'Medical' | 'Rescue' | 'Building collapse' | 'Accident' | 'Missing person' | 'Road blockage' | 'Power emergency' | 'Other' | 'None';
export type SeverityType = 'Critical' | 'High' | 'Medium' | 'Low';
export type StatusType = 'ACTIVE' | 'ESCALATED' | 'RESCUE IN PROGRESS' | 'RESOLVED' | 'UNVERIFIED' | 'CONFLICTING';
export type VerificationType = 'Verified' | 'Partially Verified' | 'Unverified' | 'Conflicting' | 'Unknown';
export type ProcessingStatus = 'RECEIVED' | 'ANALYZING' | 'UNDERSTOOD' | 'EXTRACTED' | 'MATCHED' | 'UPDATED' | 'FLAGGED' | 'NOISE';

export interface IncidentUpdate {
  id: number;
  incident_id: string;
  timestamp: string;
  update_type: string;
  description: string;
  actor: 'AI' | 'RESPONDER';
  evidence?: string;
  source_report_id?: string;
  previous_state?: Record<string, any>;
  new_state?: Record<string, any>;
}

export interface IncidentConflict {
  id: number;
  incident_id: string;
  report_id: string;
  field_name: string;
  existing_value: string;
  conflicting_value: string;
  confidence: number;
  status: 'PENDING_REVIEW' | 'RESOLVED_USE_LATEST' | 'RESOLVED_KEEP_EXISTING' | 'RESOLVED_MANUAL';
  created_at: string;
}

export interface Incident {
  id: string;
  title: string;
  emergency_type: EmergencyType;
  severity: SeverityType;
  status: StatusType;
  verification: VerificationType;
  primary_resource: string;
  people_affected: number;
  vulnerable_people?: string;
  location_name?: string;
  interpreted_location?: string;
  landmark?: string;
  best_known_location: string;
  location_confidence: number;
  latitude: number;
  longitude: number;
  uncertainty_radius_m: number;
  summary: string;
  confidence: number;
  report_count: number;
  last_escalation_reason?: string;
  created_at: string;
  updated_at: string;
  updates?: IncidentUpdate[];
  conflicts?: IncidentConflict[];
  source_reports?: RawReport[];
}

export interface RawReport {
  id: string;
  source: SourceType;
  timestamp: string;
  raw_text: string;
  processing_status: ProcessingStatus;
  is_emergency: boolean;
  is_relevant: boolean;
  is_noise: boolean;
  is_rumor: boolean;
  emergency_type: EmergencyType;
  urgency: SeverityType;
  verification: VerificationType;
  location_raw?: string;
  location_interpreted?: string;
  landmark?: string;
  people_affected?: string;
  vulnerable_people?: string;
  resource_needed?: string;
  status_signal?: string;
  evidence?: string;
  confidence: number;
  matched_incident_id?: string;
  match_confidence: number;
  match_reason?: string;
  match_status: string;
  created_at: string;
}

export interface AnalyticsSummary {
  total_reports: number;
  emergency_reports: number;
  noise_filtered: number;
  duplicate_reports_merged: number;
  underlying_incidents: number;
  active_incidents: number;
  critical_incidents: number;
  rescue_in_progress: number;
  resolved_incidents: number;
  unverified_reports: number;
  conflicting_reports: number;
  total_people_affected: number;
  compression_ratio: number;
  reports_by_source: Record<string, number>;
  incidents_by_type: Record<string, number>;
  incidents_by_severity: Record<string, number>;
  incidents_by_status: Record<string, number>;
  recent_activity_timeline: Array<{
    id: number;
    incident_id: string;
    timestamp: string;
    update_type: string;
    description: string;
    actor: string;
  }>;
}

export interface DemoStage {
  stage: number;
  title: string;
  raw_text: string;
  source: SourceType;
  expected_action: string;
}

export interface AuditLog {
  id: number;
  timestamp: string;
  action: string;
  actor: string;
  source?: string;
  incident_id?: string;
  report_id?: string;
  previous_state?: string;
  new_state?: string;
  notes?: string;
}
