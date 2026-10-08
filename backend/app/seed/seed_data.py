import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.incident import Incident, IncidentUpdate, IncidentConflict
from app.models.report import RawReport
from app.models.audit import AuditLog
from app.models.user import User
from app.database import Base, engine

def seed_database(db: Session, include_velachery_demo: bool = False):
    """
    Seeds database with 20+ underlying incidents and 100+ raw reports,
    demonstrating information compression, noise filtering, conflicts,
    vulnerabilities, and multi-channel input.
    """
    # Clear existing data
    db.query(AuditLog).delete()
    db.query(IncidentConflict).delete()
    db.query(IncidentUpdate).delete()
    db.query(RawReport).delete()
    db.query(Incident).delete()
    db.query(User).delete()
    db.commit()

    # Seed Default User
    op_user = User(
        username="commander_karthik",
        full_name="Commander Karthik R.",
        role="COMMAND_OPERATOR",
        badge_number="CR-904"
    )
    db.add(op_user)
    db.commit()

    base_time = datetime.datetime.utcnow() - datetime.timedelta(hours=6)

    # -------------------------------------------------------------
    # 20+ Realistic Diverse Incidents
    # -------------------------------------------------------------
    incidents_def = [
        {
            "id": "INC-1001",
            "title": "Severe Inundation & Trapped Citizens at Velachery MRTS",
            "emergency_type": "Flood",
            "severity": "Critical",
            "status": "ESCALATED",
            "verification": "Verified",
            "primary_resource": "Inflatable Rescue Boats & NDRF + Medical Support",
            "people_affected": 10,
            "vulnerable_people": "1 Elderly Person (Diabetic/Insulin Needed), 2 Children",
            "location_name": "Velachery MRTS West Gate",
            "interpreted_location": "Velachery MRTS Station",
            "landmark": "West Gate & Backside Road",
            "best_known_location": "Velachery MRTS Station — West Gate",
            "location_confidence": 0.94,
            "latitude": 12.9796, "longitude": 80.2185,
            "uncertainty_radius_m": 120.0,
            "summary": "Rapid water level rise (4.5 ft) near Velachery MRTS West Gate. 10 citizens trapped on upper ground floor including a vulnerable elderly person requiring insulin.",
            "confidence": 0.96,
            "report_count": 8,
            "last_escalation_reason": "People affected increased from 6 to 10 and vulnerable elderly person with insulin dependency detected."
        },
        {
            "id": "INC-1002",
            "title": "Hospital Access Submersion at Tambaram Sanatorium",
            "emergency_type": "Flood",
            "severity": "Critical",
            "status": "RESCUE IN PROGRESS",
            "verification": "Verified",
            "primary_resource": "High-Clearance Heavy Ambulance & SDRF",
            "people_affected": 15,
            "vulnerable_people": "3 Bedridden Dialysis Patients, 1 Pregnant Woman",
            "location_name": "Near Hindu Mission Hospital GST Road",
            "interpreted_location": "Tambaram Railway Hub",
            "landmark": "Sanatorium GST Road",
            "best_known_location": "Tambaram Railway Hub — Sanatorium",
            "location_confidence": 0.91,
            "latitude": 12.9249, "longitude": 80.1000,
            "uncertainty_radius_m": 180.0,
            "summary": "Chest-deep water logging cut off hospital approach corridor. Dialysis patients requiring emergency transit.",
            "confidence": 0.92,
            "report_count": 7,
            "last_escalation_reason": "Critical medical patients trapped in transport vehicle."
        },
        {
            "id": "INC-1003",
            "title": "Transformer Explosion & Fire at T. Nagar Usman Road",
            "emergency_type": "Fire",
            "severity": "Critical",
            "status": "RESCUE IN PROGRESS",
            "verification": "Verified",
            "primary_resource": "Fire Response Unit (2 Tenders) & EB Line Crew",
            "people_affected": 8,
            "vulnerable_people": "Shop workers trapped in basement textile shop",
            "location_name": "Opposite Panagal Park South Usman Flyover",
            "interpreted_location": "T. Nagar Commercial Hub",
            "landmark": "Usman Road",
            "best_known_location": "T. Nagar Commercial Hub — Usman Road",
            "location_confidence": 0.95,
            "latitude": 13.0418, "longitude": 80.2341,
            "uncertainty_radius_m": 100.0,
            "summary": "Commercial street transformer burst resulting in smoke filling ground floor garment complex.",
            "confidence": 0.95,
            "report_count": 9,
            "last_escalation_reason": "Smoke spreading into adjacent residential units."
        },
        {
            "id": "INC-1004",
            "title": "Bridge Approach Breach at Saidapet Adyar Crossing",
            "emergency_type": "Flood",
            "severity": "High",
            "status": "ACTIVE",
            "verification": "Verified",
            "primary_resource": "Traffic Police Barricades & Flood Warning Team",
            "people_affected": 4,
            "vulnerable_people": "None reported",
            "location_name": "Saidapet Bridge Adyar Riverbank",
            "interpreted_location": "Saidapet Adyar Crossing",
            "landmark": "Saidapet Bridge",
            "best_known_location": "Saidapet Adyar Crossing — Saidapet Bridge",
            "location_confidence": 0.89,
            "latitude": 13.0210, "longitude": 80.2231,
            "uncertainty_radius_m": 220.0,
            "summary": "Adyar river flow overflowed causeway; two small vehicles stalled in middle of crossing.",
            "confidence": 0.88,
            "report_count": 6,
            "last_escalation_reason": None
        },
        {
            "id": "INC-1005",
            "title": "Old Residential Wall Collapse at Madipakkam Kuberan Nagar",
            "emergency_type": "Building collapse",
            "severity": "Critical",
            "status": "RESCUE IN PROGRESS",
            "verification": "Verified",
            "primary_resource": "NDRF Search & Rescue + Ambulance",
            "people_affected": 5,
            "vulnerable_people": "1 Elderly Woman trapped in bedroom rubble",
            "location_name": "3rd Main Road Madipakkam Lake Side",
            "interpreted_location": "Madipakkam Lowlands",
            "landmark": "Madipakkam Lake",
            "best_known_location": "Madipakkam Lowlands — Madipakkam Lake",
            "location_confidence": 0.86,
            "latitude": 12.9647, "longitude": 80.1961,
            "uncertainty_radius_m": 150.0,
            "summary": "Compounded wall and portico collapsed due to soil erosion from continuous rain.",
            "confidence": 0.90,
            "report_count": 6,
            "last_escalation_reason": "Live voice contact made with elderly woman under debris."
        },
        {
            "id": "INC-1006",
            "title": "Lowland Inundation at Mudichur Flood Plain",
            "emergency_type": "Flood",
            "severity": "High",
            "status": "ACTIVE",
            "verification": "Partially Verified",
            "primary_resource": "Inflatable Rescue Boats & Evacuation Team",
            "people_affected": 24,
            "vulnerable_people": "6 Children, 4 Senior Citizens",
            "location_name": "Varadharajapuram Mudichur Road",
            "interpreted_location": "Mudichur Flood Plain",
            "landmark": "Mudichur Road",
            "best_known_location": "Mudichur Flood Plain — Mudichur Road",
            "location_confidence": 0.88,
            "latitude": 12.9056, "longitude": 80.0708,
            "uncertainty_radius_m": 350.0,
            "summary": "Water entered over 12 row houses; residents assembled on terraces awaiting evacuation boats.",
            "confidence": 0.85,
            "report_count": 8,
            "last_escalation_reason": "Water height exceeded 3.5 feet."
        },
        {
            "id": "INC-1007",
            "title": "Multi-Vehicle Pileup at Guindy Kathipara Flyover",
            "emergency_type": "Accident",
            "severity": "High",
            "status": "RESOLVED",
            "verification": "Verified",
            "primary_resource": "Ambulance & Heavy Traffic Tow Crane",
            "people_affected": 6,
            "vulnerable_people": "None",
            "location_name": "Kathipara Junction Descent towards Airport",
            "interpreted_location": "Guindy Industrial Estate & Junction",
            "landmark": "Kathipara Junction",
            "best_known_location": "Guindy Industrial Estate & Junction — Kathipara Junction",
            "location_confidence": 0.96,
            "latitude": 13.0067, "longitude": 80.2025,
            "uncertainty_radius_m": 80.0,
            "summary": "Oil spill combined with heavy rain caused 3 car collision. All 6 injured evacuated to hospital; lanes cleared.",
            "confidence": 0.98,
            "report_count": 5,
            "last_escalation_reason": None
        },
        {
            "id": "INC-1008",
            "title": "Water Logging at OMR Karapakkam IT Corridor",
            "emergency_type": "Flood",
            "severity": "Medium",
            "status": "ACTIVE",
            "verification": "Verified",
            "primary_resource": "High Capacity Dewatering Motor Pumps",
            "people_affected": 0,
            "vulnerable_people": "None",
            "location_name": "OMR Karapakkam Signal near TCS Gate",
            "interpreted_location": "OMR IT Corridor",
            "landmark": "Karapakkam",
            "best_known_location": "OMR IT Corridor — Karapakkam",
            "location_confidence": 0.89,
            "latitude": 12.9345, "longitude": 80.2312,
            "uncertainty_radius_m": 300.0,
            "summary": "Water stagnation (1.5 ft) slowing arterial traffic on both service lanes.",
            "confidence": 0.86,
            "report_count": 5,
            "last_escalation_reason": None
        },
        {
            "id": "INC-1009",
            "title": "Uprooted Banyan Tree Blocking Koyambedu Market Road",
            "emergency_type": "Road blockage",
            "severity": "Medium",
            "status": "RESCUE IN PROGRESS",
            "verification": "Verified",
            "primary_resource": "Corporation Chainsaw Team & Hydraulic Crane",
            "people_affected": 0,
            "vulnerable_people": "None",
            "location_name": "Poonamallee High Rd near CMBT Gate 2",
            "interpreted_location": "Koyambedu Hub",
            "landmark": "CMBT Bus Terminal",
            "best_known_location": "Koyambedu Hub — CMBT Bus Terminal",
            "location_confidence": 0.93,
            "latitude": 13.0694, "longitude": 80.1948,
            "uncertainty_radius_m": 100.0,
            "summary": "Large tree fell across main carriage way damaging electric poles. Clearance operation underway.",
            "confidence": 0.94,
            "report_count": 4,
            "last_escalation_reason": None
        },
        {
            "id": "INC-1010",
            "title": "Hanging High-Tension Wire at Medavakkam Junction",
            "emergency_type": "Power emergency",
            "severity": "Critical",
            "status": "ACTIVE",
            "verification": "Verified",
            "primary_resource": "TANGEDCO Emergency Power Line Crew",
            "people_affected": 3,
            "vulnerable_people": "Pedestrians cordoned off near tea stall",
            "location_name": "Medavakkam Flyover Base near Nanmangalam",
            "interpreted_location": "Medavakkam Junction",
            "landmark": "Medavakkam Flyover",
            "best_known_location": "Medavakkam Junction — Medavakkam Flyover",
            "location_confidence": 0.90,
            "latitude": 12.9181, "longitude": 80.1912,
            "uncertainty_radius_m": 120.0,
            "summary": "Live 11kV conductor snapped and dangling in knee-deep puddle with active sparking.",
            "confidence": 0.93,
            "report_count": 6,
            "last_escalation_reason": "Active sparking near waterlogged pedestrian walkway."
        },
        {
            "id": "INC-1011",
            "title": "Residential Apartment Basement Submersion in Perumbakkam",
            "emergency_type": "Flood",
            "severity": "High",
            "status": "ACTIVE",
            "verification": "Partially Verified",
            "primary_resource": "High-Head Heavy Dewatering Diesel Pumps",
            "people_affected": 40,
            "vulnerable_people": "Multiple families in ground floor apartments",
            "location_name": "Global Hospital Road Block 14",
            "interpreted_location": "Perumbakkam Resettlement",
            "landmark": "Global Hospital",
            "best_known_location": "Perumbakkam Resettlement — Global Hospital",
            "location_confidence": 0.85,
            "latitude": 12.8988, "longitude": 80.1983,
            "uncertainty_radius_m": 250.0,
            "summary": "Basement electrical room submerged in 5 feet water; power cut for 40 apartment units.",
            "confidence": 0.87,
            "report_count": 5,
            "last_escalation_reason": None
        },
        {
            "id": "INC-1012",
            "title": "Missing 7-Year-Old Child near Adyar Gandhi Nagar",
            "emergency_type": "Missing person",
            "severity": "Critical",
            "status": "ACTIVE",
            "verification": "Verified",
            "primary_resource": "Police Search Unit & Marine Volunteers",
            "people_affected": 1,
            "vulnerable_people": "7-Year-Old Child in yellow raincoat",
            "location_name": "Gandhi Nagar 4th Main near Canal",
            "interpreted_location": "Adyar Basin",
            "landmark": "Gandhi Nagar",
            "best_known_location": "Adyar Basin — Gandhi Nagar",
            "location_confidence": 0.88,
            "latitude": 13.0012, "longitude": 80.2565,
            "uncertainty_radius_m": 150.0,
            "summary": "Child separated from parents during sudden downpour near canal footpath.",
            "confidence": 0.91,
            "report_count": 4,
            "last_escalation_reason": "Proximity to open storm water drain canal."
        },
        {
            "id": "INC-1013",
            "title": "Ambulance Stuck in Flood Water near Sholinganallur",
            "emergency_type": "Medical",
            "severity": "Critical",
            "status": "RESCUE IN PROGRESS",
            "verification": "Verified",
            "primary_resource": "Heavy Rescue Vehicle & Backup 108 Ambulance",
            "people_affected": 3,
            "vulnerable_people": "1 Cardiac Patient on Oxygen in Ambulance",
            "location_name": "Sholinganallur Toll Gate OMR",
            "interpreted_location": "OMR IT Corridor",
            "landmark": "Sholinganallur Junction",
            "best_known_location": "OMR IT Corridor — Sholinganallur Junction",
            "location_confidence": 0.94,
            "latitude": 12.9010, "longitude": 80.2279,
            "uncertainty_radius_m": 110.0,
            "summary": "Emergency ambulance engine flooded while transporting cardiac patient. Backup vehicle dispatched.",
            "confidence": 0.96,
            "report_count": 5,
            "last_escalation_reason": "Patient oxygen cylinder has only 25 minutes reserve remaining."
        },
        {
            "id": "INC-1014",
            "title": "Commercial Kitchen LPG Cylinder Leak in Koyambedu",
            "emergency_type": "Fire",
            "severity": "High",
            "status": "ACTIVE",
            "verification": "Verified",
            "primary_resource": "Fire Response Unit & Gas HAZMAT Team",
            "people_affected": 12,
            "vulnerable_people": "Commercial workers evacuated to perimeter",
            "location_name": "Wholesale Vegetable Market Block D",
            "interpreted_location": "Koyambedu Hub",
            "landmark": "Koyambedu Wholesale Market",
            "best_known_location": "Koyambedu Hub — Koyambedu Wholesale Market",
            "location_confidence": 0.93,
            "latitude": 13.0694, "longitude": 80.1948,
            "uncertainty_radius_m": 140.0,
            "summary": "Commercial 19kg cylinder valve failure; heavy gas odor throughout market block.",
            "confidence": 0.92,
            "report_count": 4,
            "last_escalation_reason": None
        },
        {
            "id": "INC-1015",
            "title": "Water Logging near Thoraipakkam Toll Plaza",
            "emergency_type": "Flood",
            "severity": "Low",
            "status": "RESOLVED",
            "verification": "Verified",
            "primary_resource": "GCC Drainage Pump",
            "people_affected": 0,
            "vulnerable_people": "None",
            "location_name": "Perungudi Toll Plaza Service Road",
            "interpreted_location": "OMR IT Corridor",
            "landmark": "Perungudi Toll",
            "best_known_location": "OMR IT Corridor — Perungudi Toll",
            "location_confidence": 0.90,
            "latitude": 12.9600, "longitude": 80.2400,
            "uncertainty_radius_m": 200.0,
            "summary": "Storm water cleared after pump commissioning; traffic flowing normally.",
            "confidence": 0.95,
            "report_count": 3,
            "last_escalation_reason": None
        },
        {
            "id": "INC-1016",
            "title": "Unverified Report of Flyover Crack near Guindy",
            "emergency_type": "Building collapse",
            "severity": "Medium",
            "status": "UNVERIFIED",
            "verification": "Unverified",
            "primary_resource": "Highways Department Structural Engineer Inspection",
            "people_affected": 0,
            "vulnerable_people": "None",
            "location_name": "Olympia Tech Park Flyover Ramp",
            "interpreted_location": "Guindy Industrial Estate & Junction",
            "landmark": "Olympia Tech Park",
            "best_known_location": "Guindy Industrial Estate & Junction — Olympia Tech Park",
            "location_confidence": 0.65,
            "latitude": 13.0067, "longitude": 80.2025,
            "uncertainty_radius_m": 400.0,
            "summary": "Single social media report alleging concrete expansion joint gap. Structural team dispatched to verify.",
            "confidence": 0.42,
            "report_count": 1,
            "last_escalation_reason": None
        },
        {
            "id": "INC-1017",
            "title": "Senior Citizen Stranded on Rooftop at Madipakkam Balaiah Nagar",
            "emergency_type": "Rescue",
            "severity": "Critical",
            "status": "ACTIVE",
            "verification": "Verified",
            "primary_resource": "Inflatable Boat & SDRF",
            "people_affected": 2,
            "vulnerable_people": "2 Octogenarians (Aged 84 and 81)",
            "location_name": "Balaiah Nagar 12th Cross",
            "interpreted_location": "Madipakkam Lowlands",
            "landmark": "Balaiah Nagar",
            "best_known_location": "Madipakkam Lowlands — Balaiah Nagar",
            "location_confidence": 0.90,
            "latitude": 12.9647, "longitude": 80.1961,
            "uncertainty_radius_m": 120.0,
            "summary": "Water entered ground floor up to ceiling; elderly couple took shelter on open terrace in rain.",
            "confidence": 0.93,
            "report_count": 5,
            "last_escalation_reason": "Exposure to cold rain for over 3 hours."
        },
        {
            "id": "INC-1018",
            "title": "Flooded Underpass Trapped Car in Tambaram GST Road",
            "emergency_type": "Rescue",
            "severity": "High",
            "status": "RESCUE IN PROGRESS",
            "verification": "Verified",
            "primary_resource": "Fire & Rescue Tender with Winch",
            "people_affected": 3,
            "vulnerable_people": "1 Infant (6 Months Old)",
            "location_name": "Tambaram Sanatorium Subway",
            "interpreted_location": "Tambaram Railway Hub",
            "landmark": "Sanatorium",
            "best_known_location": "Tambaram Railway Hub — Sanatorium",
            "location_confidence": 0.92,
            "latitude": 12.9249, "longitude": 80.1000,
            "uncertainty_radius_m": 90.0,
            "summary": "Sedan vehicle hydro-locked in 4 feet underpass water; family sitting on car roof.",
            "confidence": 0.94,
            "report_count": 4,
            "last_escalation_reason": None
        },
        {
            "id": "INC-1019",
            "title": "Fallen Street Lamp & Sparking Cable in T. Nagar Ranganathan St",
            "emergency_type": "Power emergency",
            "severity": "Medium",
            "status": "ACTIVE",
            "verification": "Verified",
            "primary_resource": "EB Safety Unit",
            "people_affected": 0,
            "vulnerable_people": "None",
            "location_name": "Ranganathan Street Junction",
            "interpreted_location": "T. Nagar Commercial Hub",
            "landmark": "Ranganathan Street",
            "best_known_location": "T. Nagar Commercial Hub — Ranganathan Street",
            "location_confidence": 0.91,
            "latitude": 13.0418, "longitude": 80.2341,
            "uncertainty_radius_m": 100.0,
            "summary": "Corroded lamppost bent over pedestrian path; power line isolated remotely.",
            "confidence": 0.89,
            "report_count": 3,
            "last_escalation_reason": None
        },
        {
            "id": "INC-1020",
            "title": "Hospital Emergency Generator Fuel Depletion in Saidapet",
            "emergency_type": "Medical",
            "severity": "Critical",
            "status": "ACTIVE",
            "verification": "Verified",
            "primary_resource": "Emergency Diesel Fuel Bowsers & Police Escort",
            "people_affected": 18,
            "vulnerable_people": "18 ICU Patients on Ventilators",
            "location_name": "Saidapet Bazaar Road Govt Health Center",
            "interpreted_location": "Saidapet Adyar Crossing",
            "landmark": "Bazaar Road",
            "best_known_location": "Saidapet Adyar Crossing — Bazaar Road",
            "location_confidence": 0.93,
            "latitude": 13.0210, "longitude": 80.2231,
            "uncertainty_radius_m": 100.0,
            "summary": "Primary feeder submerged; backup generator fuel remaining under 45 minutes.",
            "confidence": 0.97,
            "report_count": 5,
            "last_escalation_reason": "Critical ICU life-support fuel constraint."
        }
    ]

    for inc_data in incidents_def:
        inc = Incident(**inc_data, created_at=base_time, updated_at=base_time + datetime.timedelta(minutes=30))
        db.add(inc)
        
        # Add initial update timeline
        upd = IncidentUpdate(
            incident_id=inc.id,
            timestamp=base_time,
            update_type="CREATED",
            description=f"Incident established from initial report: {inc.title}.",
            actor="AI",
            evidence=inc.summary,
            new_state={"status": inc.status, "severity": inc.severity, "people": inc.people_affected}
        )
        db.add(upd)

        if inc.last_escalation_reason:
            upd_esc = IncidentUpdate(
                incident_id=inc.id,
                timestamp=base_time + datetime.timedelta(minutes=20),
                update_type="ESCALATED" if inc.severity == "Critical" else "STATUS_CHANGED",
                description=inc.last_escalation_reason,
                actor="AI",
                evidence=inc.last_escalation_reason,
                new_state={"status": inc.status, "severity": inc.severity}
            )
            db.add(upd_esc)

    db.commit()

    # -------------------------------------------------------------
    # 100+ Raw Incoming Reports across all channels
    # -------------------------------------------------------------
    raw_reports_def = [
        # Velachery Cluster (INC-1001) - 8 reports
        {"id": "REP-1001", "source": "WHATSAPP", "text": "6 people trapped near Velachery MRTS west gate. Water is waist deep.", "match": "INC-1001", "type": "Flood", "urg": "High", "p": "6", "v": "Verified"},
        {"id": "REP-1002", "source": "SMS", "text": "Velachery MRTS station backside, water entered residential house ground floor. 6 people stuck.", "match": "INC-1001", "type": "Flood", "urg": "High", "p": "6", "v": "Verified"},
        {"id": "REP-1003", "source": "SOCIAL_MEDIA", "text": "Same place near Velachery MRTS, water has increased rapidly. 10 people now trapped!", "match": "INC-1001", "type": "Flood", "urg": "Critical", "p": "10", "v": "Verified"},
        {"id": "REP-1004", "source": "AUDIO", "text": "Emergency call! Elderly diabetic person is still inside near Velachery station west gate and needs insulin immediately.", "match": "INC-1001", "type": "Flood", "urg": "Critical", "p": "10", "v": "Verified"},
        {"id": "REP-1005", "source": "WHATSAPP", "text": "Water is rising fast near MRTS Vijayanagar side. Please send boats urgently.", "match": "INC-1001", "type": "Flood", "urg": "Critical", "p": "10", "v": "Verified"},
        {"id": "REP-1006", "source": "MANUAL", "text": "Control Room note: NDRF team with inflatable boat dispatched to Velachery MRTS West Gate.", "match": "INC-1001", "type": "Rescue", "urg": "Critical", "p": "10", "v": "Verified"},
        {"id": "REP-1007", "source": "SMS", "text": "Two small children also with the family near Velachery MRTS parking side.", "match": "INC-1001", "type": "Flood", "urg": "Critical", "p": "10", "v": "Verified"},
        {"id": "REP-1008", "source": "SOCIAL_MEDIA", "text": "Velachery MRTS flood rescue in progress, NDRF boat reached the gate area.", "match": "INC-1001", "type": "Rescue", "urg": "Critical", "p": "10", "v": "Verified"},

        # Tambaram Hospital Cluster (INC-1002) - 7 reports
        {"id": "REP-1009", "source": "AUDIO", "text": "Hindu Mission Hospital entrance near Tambaram Sanatorium is submerged. 3 dialysis patients stuck in ambulance.", "match": "INC-1002", "type": "Flood", "urg": "Critical", "p": "15", "v": "Verified"},
        {"id": "REP-1010", "source": "WHATSAPP", "text": "Tambaram GST road outside hospital has 4 feet water. Patients cannot enter casualty.", "match": "INC-1002", "type": "Flood", "urg": "Critical", "p": "15", "v": "Verified"},
        {"id": "REP-1011", "source": "SMS", "text": "Pregnant woman in labor stuck near Tambaram Sanatorium signal. Urgent medical vehicle needed.", "match": "INC-1002", "type": "Medical", "urg": "Critical", "p": "15", "v": "Verified"},
        {"id": "REP-1012", "source": "SOCIAL_MEDIA", "text": "Avoid Tambaram GST Road near Hindu Mission, full water logging, rescue team helping patients.", "match": "INC-1002", "type": "Flood", "urg": "High", "p": "15", "v": "Verified"},
        {"id": "REP-1013", "source": "MANUAL", "text": "Field update: High clearance military truck deployed for hospital corridor evacuation at Tambaram.", "match": "INC-1002", "type": "Rescue", "urg": "Critical", "p": "15", "v": "Verified"},
        {"id": "REP-1014", "source": "AUDIO", "text": "15 people assembled inside hospital ground lobby, water touching steps.", "match": "INC-1002", "type": "Flood", "urg": "High", "p": "15", "v": "Verified"},
        {"id": "REP-1015", "source": "WHATSAPP", "text": "Water receding slowly near Sanatorium GST road but still critical for ambulances.", "match": "INC-1002", "type": "Flood", "urg": "Medium", "p": "15", "v": "Verified"},

        # T. Nagar Transformer Fire Cluster (INC-1003) - 9 reports
        {"id": "REP-1016", "source": "AUDIO", "text": "Transformer burst on Usman Road T Nagar near Panagal Park! Heavy black smoke coming into shops.", "match": "INC-1003", "type": "Fire", "urg": "Critical", "p": "8", "v": "Verified"},
        {"id": "REP-1017", "source": "WHATSAPP", "text": "Flames seen near South Usman Flyover textile building. Fire engine needed immediately!", "match": "INC-1003", "type": "Fire", "urg": "Critical", "p": "8", "v": "Verified"},
        {"id": "REP-1018", "source": "SMS", "text": "About 8 staff trapped in basement of T Nagar shop due to thick smoke.", "match": "INC-1003", "type": "Fire", "urg": "Critical", "p": "8", "v": "Verified"},
        {"id": "REP-1019", "source": "SOCIAL_MEDIA", "text": "Massive fire near Usman Road Panagal park side. Please clear road for fire brigade.", "match": "INC-1003", "type": "Fire", "urg": "High", "p": "8", "v": "Verified"},
        {"id": "REP-1020", "source": "MANUAL", "text": "Two fire engines on site at T Nagar Usman Road. EB line trip confirmed.", "match": "INC-1003", "type": "Fire", "urg": "High", "p": "8", "v": "Verified"},
        {"id": "REP-1021", "source": "AUDIO", "text": "Smoke inhalation reported for 2 persons, ambulance reached Panagal park junction.", "match": "INC-1003", "type": "Medical", "urg": "Critical", "p": "8", "v": "Verified"},
        {"id": "REP-1022", "source": "WHATSAPP", "text": "Basement workers being evacuated with breathing masks at T Nagar.", "match": "INC-1003", "type": "Rescue", "urg": "High", "p": "8", "v": "Verified"},
        {"id": "REP-1023", "source": "SMS", "text": "Fire in T Nagar transformer brought under control, cooling operation active.", "match": "INC-1003", "type": "Fire", "urg": "Medium", "p": "8", "v": "Verified"},
        {"id": "REP-1024", "source": "SOCIAL_MEDIA", "text": "Usman road traffic diverted via GN Chetty road due to fire response.", "match": "INC-1003", "type": "Fire", "urg": "Medium", "p": "8", "v": "Verified"},

        # Saidapet Adyar River Breach (INC-1004) - 6 reports
        {"id": "REP-1025", "source": "WHATSAPP", "text": "Water overflowing Saidapet Bridge. Two cars stuck in middle.", "match": "INC-1004", "type": "Flood", "urg": "High", "p": "4", "v": "Verified"},
        {"id": "REP-1026", "source": "AUDIO", "text": "Saidapet Adyar riverbank water level reached dangerous mark. 4 passengers inside car.", "match": "INC-1004", "type": "Flood", "urg": "High", "p": "4", "v": "Verified"},
        {"id": "REP-1027", "source": "SMS", "text": "Police barricading Saidapet Bridge entrance from Guindy side.", "match": "INC-1004", "type": "Flood", "urg": "Medium", "p": "4", "v": "Verified"},
        {"id": "REP-1028", "source": "SOCIAL_MEDIA", "text": "Do not take Saidapet causeway, Adyar river overflowing.", "match": "INC-1004", "type": "Flood", "urg": "High", "p": "4", "v": "Verified"},
        {"id": "REP-1029", "source": "MANUAL", "text": "Tow team secured both stalled vehicles at Saidapet bridge; passengers safe.", "match": "INC-1004", "type": "Rescue", "urg": "Medium", "p": "4", "v": "Verified"},
        {"id": "REP-1030", "source": "WHATSAPP", "text": "River current very fast near Saidapet Metro pillar base.", "match": "INC-1004", "type": "Flood", "urg": "High", "p": "4", "v": "Verified"},

        # Madipakkam Wall Collapse (INC-1005) - 6 reports
        {"id": "REP-1031", "source": "AUDIO", "text": "House wall collapsed near Madipakkam Lake Kuberan Nagar! 5 family members inside.", "match": "INC-1005", "type": "Building collapse", "urg": "Critical", "p": "5", "v": "Verified"},
        {"id": "REP-1032", "source": "WHATSAPP", "text": "Elderly grandmother is trapped under bedroom rubble at Madipakkam Kuberan Nagar 3rd main road.", "match": "INC-1005", "type": "Building collapse", "urg": "Critical", "p": "5", "v": "Verified"},
        {"id": "REP-1033", "source": "SMS", "text": "Neighbors trying to clear bricks at Madipakkam collapse site. Need NDRF rescue team immediately.", "match": "INC-1005", "type": "Rescue", "urg": "Critical", "p": "5", "v": "Verified"},
        {"id": "REP-1034", "source": "SOCIAL_MEDIA", "text": "Building wall collapse in Madipakkam near lake side, ambulance requested.", "match": "INC-1005", "type": "Building collapse", "urg": "High", "p": "5", "v": "Verified"},
        {"id": "REP-1035", "source": "MANUAL", "text": "NDRF search team deployed with cutters at Madipakkam Kuberan Nagar.", "match": "INC-1005", "type": "Rescue", "urg": "Critical", "p": "5", "v": "Verified"},
        {"id": "REP-1036", "source": "AUDIO", "text": "Rescue team safely extracted grandmother from Madipakkam debris. First aid given.", "match": "INC-1005", "type": "Medical", "urg": "High", "p": "5", "v": "Verified"},

        # Mudichur Inundation (INC-1006) - 8 reports
        {"id": "REP-1037", "source": "SMS", "text": "Mudichur Varadharajapuram completely flooded, 24 people marooned in row houses.", "match": "INC-1006", "type": "Flood", "urg": "High", "p": "24", "v": "Verified"},
        {"id": "REP-1038", "source": "WHATSAPP", "text": "Water rising above 3 feet on Mudichur Road. 6 children and elderly people on roof.", "match": "INC-1006", "type": "Flood", "urg": "High", "p": "24", "v": "Verified"},
        {"id": "REP-1039", "source": "AUDIO", "text": "Please send rescue boats to Varadharajapuram Mudichur, no drinking water or food for 12 hours.", "match": "INC-1006", "type": "Flood", "urg": "Critical", "p": "24", "v": "Verified"},
        {"id": "REP-1040", "source": "SOCIAL_MEDIA", "text": "Mudichur families need boat evacuation urgently. Water touching ground floor lintel.", "match": "INC-1006", "type": "Flood", "urg": "High", "p": "24", "v": "Verified"},
        {"id": "REP-1041", "source": "WHATSAPP", "text": "Relief camp established at Mudichur higher secondary school.", "match": "INC-1006", "type": "Flood", "urg": "Medium", "p": "24", "v": "Verified"},
        {"id": "REP-1042", "source": "SMS", "text": "SDRF boat batch 1 reached Mudichur Varadharajapuram street 4.", "match": "INC-1006", "type": "Rescue", "urg": "High", "p": "24", "v": "Verified"},
        {"id": "REP-1043", "source": "AUDIO", "text": "12 persons evacuated from Mudichur to relief center so far.", "match": "INC-1006", "type": "Rescue", "urg": "High", "p": "24", "v": "Verified"},
        {"id": "REP-1044", "source": "SOCIAL_MEDIA", "text": "Water level steady in Mudichur, second rescue boat active.", "match": "INC-1006", "type": "Flood", "urg": "Medium", "p": "24", "v": "Verified"},

        # Guindy Kathipara Crash (INC-1007) - 5 reports (RESOLVED)
        {"id": "REP-1045", "source": "AUDIO", "text": "Multiple cars crashed on Kathipara junction flyover ramp due to oil spill and rain.", "match": "INC-1007", "type": "Accident", "urg": "High", "p": "6", "v": "Verified"},
        {"id": "REP-1046", "source": "WHATSAPP", "text": "Kathipara flyover blocked towards airport. 6 people injured in 3 car collision.", "match": "INC-1007", "type": "Accident", "urg": "High", "p": "6", "v": "Verified"},
        {"id": "REP-1047", "source": "SMS", "text": "Ambulances arrived at Kathipara Guindy. All injured shifted to Chromepet hospital.", "match": "INC-1007", "type": "Accident", "urg": "Medium", "p": "6", "v": "Verified"},
        {"id": "REP-1048", "source": "SOCIAL_MEDIA", "text": "Heavy tow crane clearing damaged cars on Kathipara flyover.", "match": "INC-1007", "type": "Accident", "urg": "Low", "p": "6", "v": "Verified"},
        {"id": "REP-1049", "source": "MANUAL", "text": "Kathipara junction completely cleared and sand spread on oil patch. All safe.", "match": "INC-1007", "type": "Accident", "urg": "Low", "p": "6", "v": "Verified"},

        # OMR Karapakkam Water Logging (INC-1008) - 5 reports
        {"id": "REP-1050", "source": "WHATSAPP", "text": "OMR Karapakkam signal near TCS has knee-deep water logging.", "match": "INC-1008", "type": "Flood", "urg": "Medium", "p": "0", "v": "Verified"},
        {"id": "REP-1051", "source": "SMS", "text": "Vehicles moving very slowly on OMR Karapakkam IT corridor due to water stagnation.", "match": "INC-1008", "type": "Flood", "urg": "Medium", "p": "0", "v": "Verified"},
        {"id": "REP-1052", "source": "SOCIAL_MEDIA", "text": "Water pumping started at Karapakkam OMR junction.", "match": "INC-1008", "type": "Flood", "urg": "Low", "p": "0", "v": "Verified"},
        {"id": "REP-1053", "source": "MANUAL", "text": "Corporation heavy dewatering motor deployed at Karapakkam culvert.", "match": "INC-1008", "type": "Flood", "urg": "Low", "p": "0", "v": "Verified"},
        {"id": "REP-1054", "source": "SMS", "text": "Water level dropped 6 inches at Karapakkam OMR.", "match": "INC-1008", "type": "Flood", "urg": "Low", "p": "0", "v": "Verified"},

        # Koyambedu Tree Blockage (INC-1009) - 4 reports
        {"id": "REP-1055", "source": "AUDIO", "text": "Huge tree fallen on Poonamallee High Road near Koyambedu CMBT Gate 2. Road blocked completely.", "match": "INC-1009", "type": "Road blockage", "urg": "Medium", "p": "0", "v": "Verified"},
        {"id": "REP-1056", "source": "WHATSAPP", "text": "Koyambedu CMBT road blocked by uprooted banyan tree and broken electric pole.", "match": "INC-1009", "type": "Road blockage", "urg": "Medium", "p": "0", "v": "Verified"},
        {"id": "REP-1057", "source": "SMS", "text": "Corporation chainsaw team cutting branches at Koyambedu market road.", "match": "INC-1009", "type": "Road blockage", "urg": "Low", "p": "0", "v": "Verified"},
        {"id": "REP-1058", "source": "MANUAL", "text": "Koyambedu road one lane opened for buses; full clearance in 20 mins.", "match": "INC-1009", "type": "Road blockage", "urg": "Low", "p": "0", "v": "Verified"},

        # Medavakkam Live Wire Emergency (INC-1010) - 6 reports
        {"id": "REP-1059", "source": "AUDIO", "text": "Live wire snapped and fell into water puddle near Medavakkam flyover base! Sparks flying.", "match": "INC-1010", "type": "Power emergency", "urg": "Critical", "p": "3", "v": "Verified"},
        {"id": "REP-1060", "source": "WHATSAPP", "text": "Danger of electrocution at Medavakkam junction near Nanmangalam road. Pedestrians trapped at tea shop.", "match": "INC-1010", "type": "Power emergency", "urg": "Critical", "p": "3", "v": "Verified"},
        {"id": "REP-1061", "source": "SMS", "text": "Urgent EB cutoff needed for Medavakkam flyover line! Live cable in water.", "match": "INC-1010", "type": "Power emergency", "urg": "Critical", "p": "3", "v": "Verified"},
        {"id": "REP-1062", "source": "SOCIAL_MEDIA", "text": "Stay away from Medavakkam junction, electric wire snapped.", "match": "INC-1010", "type": "Power emergency", "urg": "High", "p": "3", "v": "Verified"},
        {"id": "REP-1063", "source": "MANUAL", "text": "Substation contacted: Medavakkam feeder power turned off.", "match": "INC-1010", "type": "Power emergency", "urg": "Medium", "p": "3", "v": "Verified"},
        {"id": "REP-1064", "source": "SMS", "text": "EB line crew arrived at Medavakkam flyover to repair snapped wire.", "match": "INC-1010", "type": "Power emergency", "urg": "Low", "p": "3", "v": "Verified"},

        # Perumbakkam Apartment Submersion (INC-1011) - 5 reports
        {"id": "REP-1065", "source": "WHATSAPP", "text": "Perumbakkam Global Hospital road housing board block 14 basement filled with 5ft water.", "match": "INC-1011", "type": "Flood", "urg": "High", "p": "40", "v": "Partially Verified"},
        {"id": "REP-1066", "source": "SMS", "text": "Over 40 families without power at Perumbakkam apartment block due to flooded panel.", "match": "INC-1011", "type": "Flood", "urg": "High", "p": "40", "v": "Partially Verified"},
        {"id": "REP-1067", "source": "AUDIO", "text": "Ground floor residents in Perumbakkam need drinking water and food packets.", "match": "INC-1011", "type": "Flood", "urg": "Medium", "p": "40", "v": "Partially Verified"},
        {"id": "REP-1068", "source": "SOCIAL_MEDIA", "text": "Heavy pump requested for Perumbakkam housing board blocks.", "match": "INC-1011", "type": "Flood", "urg": "Medium", "p": "40", "v": "Partially Verified"},
        {"id": "REP-1069", "source": "MANUAL", "text": "Relief supply vehicle dispatched to Perumbakkam block 14.", "match": "INC-1011", "type": "Flood", "urg": "Low", "p": "40", "v": "Verified"},

        # Adyar Missing Child (INC-1012) - 4 reports
        {"id": "REP-1070", "source": "AUDIO", "text": "7-year-old child wearing yellow raincoat missing near Adyar Gandhi Nagar canal!", "match": "INC-1012", "type": "Missing person", "urg": "Critical", "p": "1", "v": "Verified"},
        {"id": "REP-1071", "source": "WHATSAPP", "text": "Lost boy Rahul aged 7 last seen near Gandhi Nagar 4th main bridge in Adyar.", "match": "INC-1012", "type": "Missing person", "urg": "Critical", "p": "1", "v": "Verified"},
        {"id": "REP-1072", "source": "SMS", "text": "Police search team scanning Adyar riverbank near Gandhi Nagar.", "match": "INC-1012", "type": "Missing person", "urg": "Critical", "p": "1", "v": "Verified"},
        {"id": "REP-1073", "source": "SOCIAL_MEDIA", "text": "Urgent alert: Child missing near Adyar canal. Contact police station immediately.", "match": "INC-1012", "type": "Missing person", "urg": "High", "p": "1", "v": "Verified"},

        # Sholinganallur Stuck Ambulance (INC-1013) - 5 reports
        {"id": "REP-1074", "source": "AUDIO", "text": "108 ambulance with cardiac patient hydro-locked at Sholinganallur toll gate OMR!", "match": "INC-1013", "type": "Medical", "urg": "Critical", "p": "3", "v": "Verified"},
        {"id": "REP-1075", "source": "SMS", "text": "Patient on oxygen inside stuck ambulance at Sholinganallur junction. Oxygen running low!", "match": "INC-1013", "type": "Medical", "urg": "Critical", "p": "3", "v": "Verified"},
        {"id": "REP-1076", "source": "WHATSAPP", "text": "Backup ambulance dispatched from Karapakkam to Sholinganallur toll.", "match": "INC-1013", "type": "Medical", "urg": "Critical", "p": "3", "v": "Verified"},
        {"id": "REP-1077", "source": "MANUAL", "text": "Patient safely transferred to backup 4x4 ambulance at Sholinganallur. En route to Apollo OMR.", "match": "INC-1013", "type": "Medical", "urg": "High", "p": "3", "v": "Verified"},
        {"id": "REP-1078", "source": "SOCIAL_MEDIA", "text": "Stalled ambulance towed out of floodwater at Sholinganallur junction.", "match": "INC-1013", "type": "Medical", "urg": "Low", "p": "3", "v": "Verified"},

        # Koyambedu Gas Leak (INC-1014) - 4 reports
        {"id": "REP-1079", "source": "AUDIO", "text": "Commercial gas cylinder leaking heavily in Koyambedu wholesale market Block D!", "match": "INC-1014", "type": "Fire", "urg": "High", "p": "12", "v": "Verified"},
        {"id": "REP-1080", "source": "WHATSAPP", "text": "12 market workers evacuated from block D Koyambedu due to strong LPG smell.", "match": "INC-1014", "type": "Fire", "urg": "High", "p": "12", "v": "Verified"},
        {"id": "REP-1081", "source": "SMS", "text": "Fire crew arrived with water spray to disperse gas vapor at Koyambedu market.", "match": "INC-1014", "type": "Fire", "urg": "Medium", "p": "12", "v": "Verified"},
        {"id": "REP-1082", "source": "MANUAL", "text": "Faulty commercial cylinder valve plugged and removed safely in Koyambedu.", "match": "INC-1014", "type": "Fire", "urg": "Low", "p": "12", "v": "Verified"},

        # Thoraipakkam Toll (INC-1015) - 3 reports (RESOLVED)
        {"id": "REP-1083", "source": "WHATSAPP", "text": "Water cleared at Perungudi / Thoraipakkam toll plaza service road.", "match": "INC-1015", "type": "Flood", "urg": "Low", "p": "0", "v": "Verified"},
        {"id": "REP-1084", "source": "SMS", "text": "Traffic flowing normally through OMR Perungudi toll.", "match": "INC-1015", "type": "Flood", "urg": "Low", "p": "0", "v": "Verified"},
        {"id": "REP-1085", "source": "SOCIAL_MEDIA", "text": "OMR toll plaza water drained completely. All lanes open.", "match": "INC-1015", "type": "Flood", "urg": "Low", "p": "0", "v": "Verified"},

        # Unverified Flyover Rumor (INC-1016) - 1 report (UNVERIFIED)
        {"id": "REP-1086", "source": "SOCIAL_MEDIA", "text": "Someone on Twitter said Olympia tech park flyover ramp near Guindy has a crack?! Is it true?", "match": "INC-1016", "type": "Building collapse", "urg": "Medium", "p": "0", "v": "Unverified"},

        # Madipakkam Rooftop Seniors (INC-1017) - 5 reports
        {"id": "REP-1087", "source": "AUDIO", "text": "Two senior citizens aged 84 and 81 stranded on terrace in Madipakkam Balaiah Nagar 12th cross.", "match": "INC-1017", "type": "Rescue", "urg": "Critical", "p": "2", "v": "Verified"},
        {"id": "REP-1088", "source": "WHATSAPP", "text": "Balaiah Nagar Madipakkam elderly couple shivering in rain on open roof. Water 4.5ft inside house.", "match": "INC-1017", "type": "Rescue", "urg": "Critical", "p": "2", "v": "Verified"},
        {"id": "REP-1089", "source": "SMS", "text": "Need SDRF inflatable boat at Balaiah Nagar 12th cross urgently for elderly rescue.", "match": "INC-1017", "type": "Rescue", "urg": "Critical", "p": "2", "v": "Verified"},
        {"id": "REP-1090", "source": "MANUAL", "text": "SDRF boat team dispatched to Madipakkam Balaiah Nagar.", "match": "INC-1017", "type": "Rescue", "urg": "High", "p": "2", "v": "Verified"},
        {"id": "REP-1091", "source": "AUDIO", "text": "Both elderly residents safely brought on board rescue boat at Balaiah Nagar.", "match": "INC-1017", "type": "Rescue", "urg": "High", "p": "2", "v": "Verified"},

        # Tambaram Subway Stalled Car (INC-1018) - 4 reports
        {"id": "REP-1092", "source": "AUDIO", "text": "Car trapped in Tambaram Sanatorium subway water with family and 6-month-old baby on roof!", "match": "INC-1018", "type": "Rescue", "urg": "Critical", "p": "3", "v": "Verified"},
        {"id": "REP-1093", "source": "WHATSAPP", "text": "Tambaram subway water level rising. 3 people stuck on car top.", "match": "INC-1018", "type": "Rescue", "urg": "High", "p": "3", "v": "Verified"},
        {"id": "REP-1094", "source": "SMS", "text": "Fire service winch vehicle reached Tambaram subway.", "match": "INC-1018", "type": "Rescue", "urg": "High", "p": "3", "v": "Verified"},
        {"id": "REP-1095", "source": "MANUAL", "text": "Family and infant safely evacuated from Tambaram subway vehicle.", "match": "INC-1018", "type": "Rescue", "urg": "Low", "p": "3", "v": "Verified"},

        # T. Nagar Lamppost (INC-1019) - 3 reports
        {"id": "REP-1096", "source": "WHATSAPP", "text": "Street light post bent over path on T Nagar Ranganathan Street junction.", "match": "INC-1019", "type": "Power emergency", "urg": "Medium", "p": "0", "v": "Verified"},
        {"id": "REP-1097", "source": "SMS", "text": "T Nagar Ranganathan st wire secured by EB team.", "match": "INC-1019", "type": "Power emergency", "urg": "Low", "p": "0", "v": "Verified"},
        {"id": "REP-1098", "source": "MANUAL", "text": "Post removed and pedestrian walkway safe at Ranganathan St.", "match": "INC-1019", "type": "Power emergency", "urg": "Low", "p": "0", "v": "Verified"},

        # Saidapet ICU Generator (INC-1020) - 5 reports
        {"id": "REP-1099", "source": "AUDIO", "text": "Critical fuel emergency! Saidapet Bazaar Road Govt Health Center generator has only 40 mins diesel for 18 ICU patients on ventilators!", "match": "INC-1020", "type": "Medical", "urg": "Critical", "p": "18", "v": "Verified"},
        {"id": "REP-1100", "source": "WHATSAPP", "text": "Saidapet hospital power down, backup generator fuel critically low.", "match": "INC-1020", "type": "Medical", "urg": "Critical", "p": "18", "v": "Verified"},
        {"id": "REP-1101", "source": "SMS", "text": "Police green corridor created for diesel tanker to Saidapet Health Center.", "match": "INC-1020", "type": "Medical", "urg": "Critical", "p": "18", "v": "Verified"},
        {"id": "REP-1102", "source": "MANUAL", "text": "1000L diesel delivered to Saidapet hospital; generator refueled and ICU stable.", "match": "INC-1020", "type": "Medical", "urg": "High", "p": "18", "v": "Verified"},
        {"id": "REP-1103", "source": "SOCIAL_MEDIA", "text": "Saidapet hospital power restored via emergency generator refueling.", "match": "INC-1020", "type": "Medical", "urg": "Low", "p": "18", "v": "Verified"},

        # -------------------------------------------------------------
        # Non-Emergency NOISE Reports (Filtered out from Incidents) - 12 reports
        # -------------------------------------------------------------
        {"id": "REP-1104", "source": "WHATSAPP", "text": "Is there traffic near Velachery right now?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1105", "source": "SMS", "text": "Will it rain tomorrow in Chennai? Need weather forecast.", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1106", "source": "SOCIAL_MEDIA", "text": "Where can I order food near T Nagar? Are Swiggy and Zomato working?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1107", "source": "WHATSAPP", "text": "Power cut in my street since 2 hours in Anna Nagar, normal scheduled maintenance?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1108", "source": "SMS", "text": "Is school holiday announced for tomorrow by collector?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1109", "source": "WHATSAPP", "text": "Any grocery shop open near Adyar signal to buy milk packets?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1110", "source": "SOCIAL_MEDIA", "text": "Can someone tell me if rain stopped in Tambaram area?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1111", "source": "SMS", "text": "How is the traffic condition on GST road towards airport?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1112", "source": "WHATSAPP", "text": "Where to buy vegetables near Koyambedu market right now?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1113", "source": "SOCIAL_MEDIA", "text": "Is metro train running normally from Guindy to Airport?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1114", "source": "SMS", "text": "Just checking in, is rain forecast heavy for tomorrow evening?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True},
        {"id": "REP-1115", "source": "WHATSAPP", "text": "Is there water logging near my gym in T Nagar?", "match": None, "type": "None", "urg": "Low", "p": None, "v": "Unknown", "noise": True}
    ]

    for idx, r_data in enumerate(raw_reports_def):
        r_time = base_time + datetime.timedelta(minutes=idx * 2)
        is_noise = r_data.get("noise", False)
        
        rep = RawReport(
            id=r_data["id"],
            source=r_data["source"],
            timestamp=r_time,
            raw_text=r_data["text"],
            processing_status="NOISE" if is_noise else "UPDATED",
            is_emergency=not is_noise,
            is_relevant=not is_noise,
            is_noise=is_noise,
            is_rumor=r_data["v"] == "Unverified",
            emergency_type=r_data["type"],
            urgency=r_data["urgg"] if "urgg" in r_data else r_data["urg"],
            verification=r_data["v"],
            people_affected=r_data.get("p"),
            matched_incident_id=r_data.get("match"),
            match_confidence=0.92 if r_data.get("match") else 0.0,
            match_status="AUTO_MERGED" if r_data.get("match") else ("NOISE" if is_noise else "NONE"),
            confidence=0.88 if not is_noise else 0.30,
            created_at=r_time
        )
        db.add(rep)

        # Audit log for each report
        audit = AuditLog(
            timestamp=r_time,
            action="REPORT_PROCESSED" if not is_noise else "REPORT_FILTERED_NOISE",
            actor="AI",
            source=r_data["source"],
            incident_id=r_data.get("match"),
            report_id=r_data["id"],
            previous_state="RECEIVED",
            new_state="MERGED" if r_data.get("match") else ("NOISE" if is_noise else "CREATED"),
            notes=f"Processed raw report '{r_data['id']}' via 5-part AI pipeline."
        )
        db.add(audit)

    db.commit()
    print(f"[Seed] Successfully seeded {len(incidents_def)} incidents and {len(raw_reports_def)} raw reports!")
