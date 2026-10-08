import { Incident, RawReport, AnalyticsSummary, DemoStage, AuditLog } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = {
  // Incidents
  async getIncidents(params?: {
    emergency_type?: string;
    severity?: string;
    status?: string;
    verification?: string;
    search?: string;
  }): Promise<Incident[]> {
    const query = new URLSearchParams();
    if (params?.emergency_type && params.emergency_type !== 'All') query.append('emergency_type', params.emergency_type);
    if (params?.severity && params.severity !== 'All') query.append('severity', params.severity);
    if (params?.status && params.status !== 'All') query.append('status', params.status);
    if (params?.verification && params.verification !== 'All') query.append('verification', params.verification);
    if (params?.search) query.append('search', params.search);

    const res = await fetch(`${API_BASE}/incidents?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch incidents');
    return res.json();
  },

  async getIncidentDetail(id: string): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch incident ${id}`);
    return res.json();
  },

  async updateIncident(id: string, payload: Partial<Incident> & { notes?: string }): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to update incident');
    return res.json();
  },

  async verifyIncident(id: string): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}/verify`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to verify incident');
    return res.json();
  },

  async resolveIncident(id: string, notes?: string): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}/resolve?notes=${encodeURIComponent(notes || '')}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to resolve incident');
    return res.json();
  },

  async mergeIntoIncident(payload: { target_incident_id: string; report_id?: string; reason?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/incidents/merge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to merge incident');
    return res.json();
  },

  async resolveIncidentConflict(incidentId: string, conflictId: number, payload: { action: string; manual_value?: string; notes?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/incidents/${incidentId}/conflicts/${conflictId}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to resolve conflict');
    return res.json();
  },

  // Reports
  async getReports(params?: { source?: string; emergency_type?: string; is_noise?: boolean; matched_incident_id?: string; limit?: number }): Promise<RawReport[]> {
    const query = new URLSearchParams();
    if (params?.source && params.source !== 'All') query.append('source', params.source);
    if (params?.emergency_type && params.emergency_type !== 'All') query.append('emergency_type', params.emergency_type);
    if (params?.is_noise !== undefined) query.append('is_noise', String(params.is_noise));
    if (params?.matched_incident_id) query.append('matched_incident_id', params.matched_incident_id);
    if (params?.limit) query.append('limit', String(params.limit));

    const res = await fetch(`${API_BASE}/reports?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch reports');
    return res.json();
  },

  async createReport(payload: { raw_text: string; source: string; metadata?: any }): Promise<any> {
    const res = await fetch(`${API_BASE}/reports`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to submit report');
    }
    return res.json();
  },

  async uploadFileReports(formData: FormData): Promise<any> {
    const res = await fetch(`${API_BASE}/reports/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload file');
    return res.json();
  },

  async uploadAudioReport(formData: FormData): Promise<any> {
    const res = await fetch(`${API_BASE}/reports/audio`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Failed to process audio');
    return res.json();
  },

  // Analytics & Audit
  async getAnalytics(): Promise<AnalyticsSummary> {
    const res = await fetch(`${API_BASE}/analytics`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  async getAuditLogs(params?: { actor?: string; incident_id?: string; limit?: number }): Promise<AuditLog[]> {
    const query = new URLSearchParams();
    if (params?.actor && params.actor !== 'All') query.append('actor', params.actor);
    if (params?.incident_id) query.append('incident_id', params.incident_id);
    if (params?.limit) query.append('limit', String(params.limit));

    const res = await fetch(`${API_BASE}/audit?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },

  // AI Assistant
  async queryAIAssistant(query: string, incident_id?: string): Promise<{ answer: string; sources_used: string[]; suggested_actions: string[] }> {
    const res = await fetch(`${API_BASE}/ai/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, incident_id })
    });
    if (!res.ok) throw new Error('Failed to query AI assistant');
    return res.json();
  },

  // Demo
  async getDemoStages(): Promise<DemoStage[]> {
    const res = await fetch(`${API_BASE}/demo/stages`);
    if (!res.ok) throw new Error('Failed to fetch demo stages');
    return res.json();
  },

  async executeDemoStep(stageId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/demo/step/${stageId}`, { method: 'POST' });
    if (!res.ok) throw new Error(`Failed to execute demo step ${stageId}`);
    return res.json();
  },

  async resetDemoData(): Promise<any> {
    const res = await fetch(`${API_BASE}/demo/reset`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset demo data');
    return res.json();
  }
};
