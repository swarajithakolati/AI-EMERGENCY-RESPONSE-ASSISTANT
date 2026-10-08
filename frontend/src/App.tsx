import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/layout/Header';
import { Sidebar, NavView } from './components/layout/Sidebar';
import { IncidentCard } from './components/dashboard/IncidentCard';
import { IncidentFilters } from './components/dashboard/IncidentFilters';
import { RecentUpdatesFeed } from './components/dashboard/RecentUpdatesFeed';
import { IncidentMap } from './components/map/IncidentMap';
import { IncidentDetailModal } from './components/incident-detail/IncidentDetailModal';
import { InputCenterModal } from './components/input-center/InputCenterModal';
import { LiveDemoShowcase } from './components/demo/LiveDemoShowcase';
import { AIAssistantDrawer } from './components/ai-assistant/AIAssistantDrawer';
import { HumanReviewModal } from './components/human-review/HumanReviewModal';
import { LiveReportFeed } from './components/live-feed/LiveReportFeed';
import { AnalyticsView } from './components/analytics/AnalyticsView';
import { AuditView } from './components/audit/AuditView';
import { Incident, AnalyticsSummary } from './types';
import { api } from './services/api';

export function App() {
  const [currentView, setCurrentView] = useState<NavView>('dashboard');
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Filter States
  const [search, setSearch] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('All');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('All');
  const [selectedStatus, setSelectedStatus] = useState<string>('All');
  const [selectedVerification, setSelectedVerification] = useState<string>('All');

  // Active Incident Selection / Modals
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [detailIncidentId, setDetailIncidentId] = useState<string | null>(null);

  // Modal Visibility States
  const [isDemoOpen, setIsDemoOpen] = useState<boolean>(false);
  const [isInputCenterOpen, setIsInputCenterOpen] = useState<boolean>(false);
  const [isAIAssistantOpen, setIsAIAssistantOpen] = useState<boolean>(false);
  const [isReviewQueueOpen, setIsReviewQueueOpen] = useState<boolean>(false);

  // Data fetching
  const refreshData = useCallback(async () => {
    try {
      setLoading(true);
      const [incs, anlytics] = await Promise.all([
        api.getIncidents({
          emergency_type: selectedType,
          severity: selectedSeverity,
          status: selectedStatus,
          verification: selectedVerification,
          search: search
        }),
        api.getAnalytics()
      ]);
      setIncidents(incs);
      setAnalytics(anlytics);
    } catch (e) {
      console.error('Failed to load dashboard data', e);
    } finally {
      setLoading(false);
    }
  }, [selectedType, selectedSeverity, selectedStatus, selectedVerification, search]);

  useEffect(() => {
    refreshData();
    // Auto-polling interval every 6 seconds for live feed sync
    const interval = setInterval(refreshData, 6000);
    return () => clearInterval(interval);
  }, [refreshData]);

  const handleResetFilters = () => {
    setSearch('');
    setSelectedType('All');
    setSelectedSeverity('All');
    setSelectedStatus('All');
    setSelectedVerification('All');
  };

  const handleResetData = async () => {
    if (window.confirm('Reset database to clean default seed data?')) {
      await api.resetDemoData();
      await refreshData();
    }
  };

  const handleOpenIncidentSitRep = (incidentId: string) => {
    setDetailIncidentId(incidentId);
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#090d16] text-slate-100 overflow-hidden">
      {/* Top Fixed Header */}
      <Header
        analytics={analytics}
        onOpenDemo={() => setIsDemoOpen(true)}
        onOpenInputCenter={() => setIsInputCenterOpen(true)}
        onToggleAIAssistant={() => setIsAIAssistantOpen(!isAIAssistantOpen)}
        onResetData={handleResetData}
        isAIAssistantOpen={isAIAssistantOpen}
        unresolvedConflictsCount={analytics?.conflicting_reports || 0}
        onOpenReviewQueue={() => setIsReviewQueueOpen(true)}
      />

      {/* Main App Layout */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left Navigation Sidebar */}
        <Sidebar
          currentView={currentView}
          onSelectView={setCurrentView}
          unverifiedCount={analytics?.unverified_reports || 0}
        />

        {/* Dynamic Main Workspace View */}
        <main className="flex-1 overflow-y-auto p-3 sm:p-4 bg-[#090d16] relative">
          
          {/* VIEW 1: COMMAND DASHBOARD */}
          {currentView === 'dashboard' && (
            <div className="space-y-4 max-w-[1600px] mx-auto">
              
              {/* Top Row: Map & Live Updates Stream (Side by Side) */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                {/* Left / Center Map (8 cols) */}
                <div className="lg:col-span-8 h-[340px] sm:h-[400px]">
                  <IncidentMap
                    incidents={incidents}
                    onSelectIncident={(inc) => {
                      setSelectedIncident(inc);
                      setDetailIncidentId(inc.id);
                    }}
                    selectedIncident={selectedIncident}
                  />
                </div>

                {/* Right Live Updates Feed (4 cols) */}
                <div className="lg:col-span-4 h-[340px] sm:h-[400px]">
                  <RecentUpdatesFeed
                    updates={analytics?.recent_activity_timeline || []}
                    onSelectIncident={handleOpenIncidentSitRep}
                  />
                </div>
              </div>

              {/* Bottom Row: Incident Filters & Filterable Incident Cards Grid */}
              <div className="space-y-3">
                <IncidentFilters
                  search={search}
                  onSearchChange={setSearch}
                  selectedType={selectedType}
                  onTypeChange={setSelectedType}
                  selectedSeverity={selectedSeverity}
                  onSeverityChange={setSelectedSeverity}
                  selectedStatus={selectedStatus}
                  onStatusChange={setSelectedStatus}
                  selectedVerification={selectedVerification}
                  onVerificationChange={setSelectedVerification}
                  onResetFilters={handleResetFilters}
                  totalFiltered={incidents.length}
                />

                {/* Incident Cards Grid */}
                {incidents.length === 0 ? (
                  <div className="text-center py-16 bg-slate-900/50 border border-slate-800 rounded-xl space-y-2">
                    <p className="text-sm font-semibold text-slate-300">No active incidents matching your criteria.</p>
                    <button
                      onClick={handleResetFilters}
                      className="text-xs text-blue-400 hover:text-blue-300 underline"
                    >
                      Clear filters to view all incidents
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3.5">
                    {incidents.map((incident) => (
                      <IncidentCard
                        key={incident.id}
                        incident={incident}
                        onClick={(inc) => {
                          setSelectedIncident(inc);
                          setDetailIncidentId(inc.id);
                        }}
                        isSelected={selectedIncident?.id === incident.id}
                      />
                    ))}
                  </div>
                )}
              </div>

            </div>
          )}

          {/* VIEW 2: FULL SECTOR MAP */}
          {currentView === 'map' && (
            <div className="h-full min-h-[600px] flex flex-col space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-bold text-white">Geographic Sector Command Map</h2>
                  <p className="text-xs text-slate-400">Pulsing clusters indicate critical urgency. Dashed radius shows landmark uncertainty radius.</p>
                </div>
              </div>
              <div className="flex-1 rounded-xl overflow-hidden border border-slate-800 min-h-[500px]">
                <IncidentMap
                  incidents={incidents}
                  onSelectIncident={(inc) => {
                    setSelectedIncident(inc);
                    setDetailIncidentId(inc.id);
                  }}
                  selectedIncident={selectedIncident}
                />
              </div>
            </div>
          )}

          {/* VIEW 3: LIVE REPORT STREAM */}
          {currentView === 'live-feed' && (
            <LiveReportFeed onSelectIncident={handleOpenIncidentSitRep} />
          )}

          {/* VIEW 4: MULTI-MODAL INGESTION */}
          {currentView === 'input' && (
            <div className="max-w-4xl mx-auto">
              <InputCenterModal
                onClose={() => setCurrentView('dashboard')}
                onReportIngested={() => refreshData()}
              />
            </div>
          )}

          {/* VIEW 5: VELACHERY SHOWCASE */}
          {currentView === 'demo' && (
            <div className="max-w-5xl mx-auto">
              <LiveDemoShowcase
                onClose={() => setCurrentView('dashboard')}
                onRefreshDashboard={refreshData}
                onOpenIncidentDetail={handleOpenIncidentSitRep}
              />
            </div>
          )}

          {/* VIEW 6: COMPRESSION ANALYTICS */}
          {currentView === 'analytics' && (
            <div className="max-w-6xl mx-auto">
              <AnalyticsView />
            </div>
          )}

          {/* VIEW 7: AUDIT TRAIL */}
          {currentView === 'audit' && (
            <div className="max-w-6xl mx-auto">
              <AuditView />
            </div>
          )}

        </main>

        {/* AI Responder Assistant Drawer */}
        <AIAssistantDrawer
          isOpen={isAIAssistantOpen}
          onClose={() => setIsAIAssistantOpen(false)}
          selectedIncidentId={selectedIncident?.id}
        />
      </div>

      {/* MODALS */}
      {/* 1. Incident Detail Modal */}
      {detailIncidentId && (
        <IncidentDetailModal
          incidentId={detailIncidentId}
          onClose={() => setDetailIncidentId(null)}
          onRefresh={refreshData}
        />
      )}

      {/* 2. Interactive Input Center Modal */}
      {isInputCenterOpen && (
        <InputCenterModal
          onClose={() => setIsInputCenterOpen(false)}
          onReportIngested={() => refreshData()}
        />
      )}

      {/* 3. Live Demo Mode Showcase Modal */}
      {isDemoOpen && (
        <LiveDemoShowcase
          onClose={() => setIsDemoOpen(false)}
          onRefreshDashboard={refreshData}
          onOpenIncidentDetail={handleOpenIncidentSitRep}
        />
      )}

      {/* 4. Human Review Queue Modal */}
      {isReviewQueueOpen && (
        <HumanReviewModal
          onClose={() => setIsReviewQueueOpen(false)}
          onRefresh={refreshData}
        />
      )}
    </div>
  );
}

export default App;
