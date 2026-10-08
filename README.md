# AI Emergency Response Assistant
> “Helping emergency responders understand incoming information faster.”

An AI assistant for emergency responders and control-room staff that turns **hundreds of messy, multi-channel reports into a smaller number of continuously updated, evolving incidents**.

---

## 🎯 Central Product Principle: MANY REPORTS → ONE EVOLVING INCIDENT

Emergency command centers receive overwhelming volumes of unstructured, incomplete, conflicting, and noisy reports during major disasters (floods, fires, accidents). A single emergency incident often triggers dozens of calls, WhatsApp messages, social media posts, and SMS alerts.

**The Core Principle**:
- **AI is an ASSISTANT, NOT an autonomous command authority**.
- The AI organizes incoming information, removes noise, extracts critical entities, detects duplicates, updates the single evolving incident record, and flags meaningful state changes.
- **Trained human responders remain in complete command** to verify, review, merge, override, and dispatch field resources.

---

## 🔄 The Mandatory Five-Part Pipeline

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐    ┌─────────────────┐
│  1. INGEST  │ ➔ │ 2. UNDERSTAND   │ ➔ │   3. EXTRACT    │ ➔ │   4. TRACK     │ ➔ │    5. SHOW      │
│ Multi-Modal │    │ Emergency/Noise │    │ Location/Counts │    │ Match & Evolve │    │ Responder Ops   │
└─────────────┘    └─────────────────┘    └─────────────────┘    └────────────────┘    └─────────────────┘
```

1. **INGEST**: Unified schema ingesting Audio calls (STT), WhatsApp, SMS, Social Media, Manual Dispatch, and batch CSV/JSON files.
2. **UNDERSTAND**: Identifies emergency type, urgency (*Critical, High, Medium, Low*), and automatically filters non-emergency noise (e.g. *"Is there traffic near Velachery?"*, *"Will it rain tomorrow?"*).
3. **EXTRACT**: Extracts structured casualties, vulnerable persons (*elderly, infants, diabetics/insulin, oxygen dependency*), landmarks, and primary resource needs (*Inflatable boats, Ambulance, Fire tender, Heavy crane*).
4. **TRACK**: Multi-factor matching engine (Landmarks, Spatial Proximity, Temporal Window, Semantic Overlap) that aggregates follow-up messages into one incident timeline without overwriting historical records.
5. **SHOW**: Fast, low-cognitive-load responder dashboard with Interactive Map, Incident Cards, Live Update Stream, AI Assistant, and Human Review queues.

---

## 🏆 Primary Demo Incident (Velachery Flooding Showcase)

The platform includes a dedicated **Interactive Live Demo Mode** demonstrating the complete 6-stage evolution of a single incident without ticket proliferation:

| Stage | Incoming Report | AI Operational Action | Resulting State |
|---|---|---|---|
| **1** | *"6 people trapped near Velachery MRTS."* | Ingests & creates new evolving incident record | `INC-1001` (6 People, Flood) |
| **2** | *"Same place, water has increased. 10 people now."* | Recognizes contextual landmark & anaphora. Updates headcount. | `INC-1001` (6 ➔ 10 People) |
| **3** | *"Elderly person is still inside and needs insulin."* | Detects vulnerable individual & medical dependency. Elevates severity. | Severity: `Critical`, Resource: `Medical Ambulance` |
| **4** | *"Water is rising."* | Detects environmental hazard escalation with causal evidence. | Status: `ESCALATED` |
| **5** | *"Rescue team has reached."* | Operational transition to field deployment. | Status: `RESCUE IN PROGRESS` |
| **6** | *"Everyone rescued."* | Operational mission completion. | Status: `RESOLVED` |

**All six reports appear under ONE evolving incident record.**

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. One-Click Launch
```bash
./start.sh
```
This automatically boots:
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000) (Interactive Swagger: `/docs`)
- **React Control Center**: [http://localhost:5173](http://localhost:5173)

### 2. Manual Startup

**Backend**:
```bash
cd backend
python3 -m pip install -r requirements.txt
export PYTHONPATH=.
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Acceptance Test Suite

Run the full automated test suite verifying all 10 hackathon acceptance criteria:

```bash
PYTHONPATH=backend python3 -m pytest backend/app/tests/test_acceptance.py -v
```

### Verified Test Cases (10/10 Passed):
- `test_1_new_incident_creation`: Verifies initial report establishes one incident.
- `test_2_same_incident_evolution_people_count`: Verifies second report updates headcount (6 ➔ 10).
- `test_3_vulnerable_person_and_medical_need`: Verifies vulnerability detection & medical resource escalation.
- `test_4_environmental_escalation`: Verifies water rising triggers escalation state.
- `test_5_rescue_in_progress_status`: Verifies rescue team arrival transitions to `RESCUE IN PROGRESS`.
- `test_6_resolution_status`: Verifies field completion transitions to `RESOLVED`.
- `test_7_non_emergency_noise_filtering`: Verifies non-emergency queries are filtered into audit logs without creating incident tickets.
- `test_8_conflicting_people_count_detection`: Verifies divergent headcounts trigger human review conflict flag.
- `test_9_uncertain_location_handling`: Verifies fuzzy locations display best-known confidence without false precision.
- `test_10_multi_report_clustering_compression`: Verifies multiple descriptive reports collapse into 1 incident.

---

## 🛠️ Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Leaflet / React-Leaflet, Recharts.
- **Backend**: Python FastAPI, SQLAlchemy, Pydantic v2, SQLite / PostgreSQL, Uvicorn.
- **AI Intelligence Engine**: Multi-factor NLP classifier, Regex entity extractor, Geographic Landmark parser, and optional LLM integration (Gemini / OpenAI).
- **Audio / STT**: Web Speech API + backend simulated audio processing.

---

## 📡 API Reference Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/reports` | Ingests a raw report across any supported channel |
| `POST` | `/api/reports/batch` | Batch ingestion of multiple reports |
| `POST` | `/api/reports/audio` | Audio call transcription & ingestion |
| `POST` | `/api/reports/upload` | CSV / JSON batch file upload |
| `GET` | `/api/reports` | List raw reports with filtering |
| `GET` | `/api/incidents` | List evolving incidents with search & filters |
| `GET` | `/api/incidents/{id}` | Detailed incident sitrep, timeline, & sources |
| `PATCH` | `/api/incidents/{id}` | Manual responder state override & notes |
| `POST` | `/api/incidents/{id}/verify` | Human responder verifies authenticity |
| `POST` | `/api/incidents/{id}/resolve` | Marks incident as resolved |
| `POST` | `/api/incidents/merge` | Merges report into incident |
| `POST` | `/api/incidents/{id}/conflicts/{id}/resolve` | Resolves conflicting information |
| `POST` | `/api/ai/query` | Grounded AI responder assistant Q&A |
| `GET` | `/api/analytics` | Compression and operational distribution metrics |
| `GET` | `/api/audit` | Chronological immutable audit trail |
| `POST` | `/api/demo/step/{id}` | Executes step (1-6) of Velachery live showcase |
| `POST` | `/api/demo/reset` | Resets database to default seed state |

---

## 🔒 Safety & Principle Summary
1. **AI is an Assistant**: Field teams are never autonomously dispatched without dispatcher oversight.
2. **Honest Location Confidence**: Uncertainty is clearly surfaced as confidence scores and radius bounding.
3. **Historical Integrity**: Previous states are preserved chronologically in the timeline, never destroyed.
