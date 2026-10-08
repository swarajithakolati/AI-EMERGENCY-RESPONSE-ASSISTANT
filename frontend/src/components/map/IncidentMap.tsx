import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Incident } from '../../types';
import { Users, AlertTriangle, ShieldCheck, ExternalLink } from 'lucide-react';

interface IncidentMapProps {
  incidents: Incident[];
  onSelectIncident: (incident: Incident) => void;
  selectedIncident?: Incident | null;
}

// Custom Leaflet DivIcon for emergency severity & status
function createCustomIcon(incident: Incident, isSelected: boolean) {
  let color = '#3b82f6'; // Blue
  let pulseClass = '';

  if (incident.severity === 'Critical') {
    color = '#ef4444'; // Red
    pulseClass = 'marker-pulse-critical';
  } else if (incident.severity === 'High') {
    color = '#f97316'; // Orange
  } else if (incident.status === 'RESOLVED') {
    color = '#10b981'; // Green
  }

  const border = isSelected ? 'border-2 border-white scale-125' : 'border border-slate-900';

  const html = `
    <div class="relative flex items-center justify-center">
      <div class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] text-white shadow-lg ${border} ${pulseClass}" style="background-color: ${color};">
        ${incident.people_affected > 0 ? incident.people_affected : '!'}
      </div>
    </div>
  `;

  return L.divIcon({
    html: html,
    className: 'custom-emergency-marker',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12]
  });
}

// Helper to recenter map when selectedIncident changes
function MapRecenter({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.flyTo(center, 13, { duration: 1.2 });
    }
  }, [center, map]);
  return null;
}

export const IncidentMap: React.FC<IncidentMapProps> = ({ incidents, onSelectIncident, selectedIncident }) => {
  const defaultCenter: [number, number] = [12.9796, 80.2185]; // Velachery Chennai center
  const center: [number, number] = selectedIncident 
    ? [selectedIncident.latitude, selectedIncident.longitude]
    : defaultCenter;

  return (
    <div className="w-full h-full min-h-[380px] rounded-xl overflow-hidden border border-slate-800 relative bg-slate-950">
      <MapContainer
        center={defaultCenter}
        zoom={12}
        scrollWheelZoom={true}
        className="w-full h-full z-10"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="dark-map-tiles"
        />

        {selectedIncident && (
          <MapRecenter center={[selectedIncident.latitude, selectedIncident.longitude]} />
        )}

        {incidents.map((inc) => {
          const isSelected = selectedIncident?.id === inc.id;
          const markerIcon = createCustomIcon(inc, isSelected);

          return (
            <React.Fragment key={inc.id}>
              {/* Uncertainty Radius Circle */}
              <Circle
                center={[inc.latitude, inc.longitude]}
                radius={inc.uncertainty_radius_m || 250}
                pathOptions={{
                  color: inc.severity === 'Critical' ? '#ef4444' : inc.status === 'RESOLVED' ? '#10b981' : '#3b82f6',
                  fillColor: inc.severity === 'Critical' ? '#ef4444' : '#3b82f6',
                  fillOpacity: isSelected ? 0.25 : 0.12,
                  weight: isSelected ? 2 : 1,
                  dashArray: inc.location_confidence < 0.7 ? '4, 4' : undefined
                }}
              />

              {/* Emergency Marker */}
              <Marker
                position={[inc.latitude, inc.longitude]}
                icon={markerIcon}
                eventHandlers={{
                  click: () => onSelectIncident(inc)
                }}
              >
                <Popup className="emergency-map-popup">
                  <div className="p-1 min-w-[200px] text-slate-900">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="font-mono font-bold text-xs bg-slate-200 px-1.5 py-0.5 rounded text-slate-800">
                        {inc.id}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded text-white ${
                        inc.severity === 'Critical' ? 'bg-red-600' : inc.severity === 'High' ? 'bg-orange-600' : 'bg-blue-600'
                      }`}>
                        {inc.severity}
                      </span>
                    </div>

                    <h4 className="font-bold text-xs leading-tight mb-1 text-slate-900">{inc.title}</h4>
                    <p className="text-[11px] text-slate-600 mb-1.5">{inc.best_known_location}</p>

                    <div className="text-[11px] bg-slate-100 p-1.5 rounded mb-2 space-y-0.5">
                      <div><strong>People Affected:</strong> {inc.people_affected}</div>
                      <div><strong>Status:</strong> {inc.status}</div>
                      {inc.vulnerable_people && (
                        <div className="text-red-700 font-semibold">⚠️ {inc.vulnerable_people}</div>
                      )}
                    </div>

                    <button
                      onClick={() => onSelectIncident(inc)}
                      className="w-full py-1 text-xs font-semibold text-center bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors flex items-center justify-center gap-1"
                    >
                      <span>Open SitRep</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Map Legend Overlay */}
      <div className="absolute top-3 right-3 z-20 bg-slate-950/90 backdrop-blur-md border border-slate-800 p-2.5 rounded-lg text-[11px] text-slate-300 space-y-1.5 shadow-xl pointer-events-auto">
        <div className="font-bold text-slate-200 text-xs border-b border-slate-800 pb-1 flex items-center justify-between gap-3">
          <span>Map Legend</span>
          <span className="text-[10px] text-slate-500 font-mono">SECTOR RADII</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></span>
          <span>Critical Emergency</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-orange-500"></span>
          <span>High Urgency</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-blue-500"></span>
          <span>Active / Moderate</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
          <span>Resolved Site</span>
        </div>
        <div className="text-[10px] text-slate-400 pt-1 border-t border-slate-800/80">
          Dashed circles = Inferred location uncertainty
        </div>
      </div>
    </div>
  );
};
