import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.incident import Incident, IncidentConflict
from app.models.report import RawReport
from app.engine.pipeline import process_incoming_report
from app.engine.location_parser import parse_location_intelligence

# Setup in-memory SQLite database for clean isolated acceptance testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_1_new_incident_creation():
    """TEST 1: Submit '6 people trapped near Velachery MRTS.' -> Expected: One new incident."""
    db = TestingSessionLocal()
    res = process_incoming_report("6 people trapped near Velachery MRTS.", "WHATSAPP", db)
    
    assert res["status"] == "SUCCESS"
    inc = res["incident"]
    assert inc is not None
    assert "Velachery" in inc.best_known_location
    assert inc.people_affected == 6
    assert inc.emergency_type in ["Flood", "Rescue"]
    assert db.query(Incident).count() == 1
    db.close()

def test_2_same_incident_evolution_people_count():
    """TEST 2: Submit 'Same place, water has increased. 10 people now.' -> Expected: Same incident, People count becomes 10."""
    db = TestingSessionLocal()
    # Step 1
    res1 = process_incoming_report("6 people trapped near Velachery MRTS.", "WHATSAPP", db)
    inc_id = res1["incident"].id
    
    # Step 2
    res2 = process_incoming_report("Same place, water has increased. 10 people now.", "SMS", db)
    
    assert db.query(Incident).count() == 1
    inc = db.query(Incident).filter(Incident.id == inc_id).first()
    assert inc.people_affected == 10
    assert inc.report_count == 2
    db.close()

def test_3_vulnerable_person_and_medical_need():
    """TEST 3: Submit 'Elderly person is still inside and needs insulin.' -> Expected: Same incident, Vulnerable person detected, Medical resource detected."""
    db = TestingSessionLocal()
    res1 = process_incoming_report("6 people trapped near Velachery MRTS.", "WHATSAPP", db)
    inc_id = res1["incident"].id
    
    res3 = process_incoming_report("Elderly person is still inside and needs insulin.", "AUDIO", db)
    inc = db.query(Incident).filter(Incident.id == inc_id).first()
    
    assert db.query(Incident).count() == 1
    assert inc.vulnerable_people is not None
    assert "Elderly" in inc.vulnerable_people or "Insulin" in inc.vulnerable_people
    assert "Medical" in inc.primary_resource or "Ambulance" in inc.primary_resource
    assert inc.severity == "Critical"
    db.close()

def test_4_environmental_escalation():
    """TEST 4: Submit 'Water is rising.' -> Expected: Possible escalation."""
    db = TestingSessionLocal()
    res1 = process_incoming_report("6 people trapped near Velachery MRTS.", "WHATSAPP", db)
    inc_id = res1["incident"].id
    
    res4 = process_incoming_report("Water is rising fast near the same place.", "SOCIAL_MEDIA", db)
    inc = db.query(Incident).filter(Incident.id == inc_id).first()
    
    assert db.query(Incident).count() == 1
    assert inc.status in ["ESCALATED", "ACTIVE"]
    assert inc.severity in ["High", "Critical"]
    db.close()

def test_5_rescue_in_progress_status():
    """TEST 5: Submit 'Rescue team has reached.' -> Expected: Status = RESCUE IN PROGRESS."""
    db = TestingSessionLocal()
    res1 = process_incoming_report("6 people trapped near Velachery MRTS.", "WHATSAPP", db)
    inc_id = res1["incident"].id
    
    res5 = process_incoming_report("Rescue team has reached the same location with boats.", "MANUAL", db)
    inc = db.query(Incident).filter(Incident.id == inc_id).first()
    
    assert db.query(Incident).count() == 1
    assert inc.status == "RESCUE IN PROGRESS"
    db.close()

def test_6_resolution_status():
    """TEST 6: Submit 'Everyone rescued.' -> Expected: Status = RESOLVED."""
    db = TestingSessionLocal()
    res1 = process_incoming_report("6 people trapped near Velachery MRTS.", "WHATSAPP", db)
    inc_id = res1["incident"].id
    
    res6 = process_incoming_report("Everyone rescued safely from here.", "AUDIO", db)
    inc = db.query(Incident).filter(Incident.id == inc_id).first()
    
    assert db.query(Incident).count() == 1
    assert inc.status == "RESOLVED"
    db.close()

def test_7_non_emergency_noise_filtering():
    """TEST 7: Submit 'Is there traffic near Velachery?' -> Expected: NON-EMERGENCY / NOISE. No new incident."""
    db = TestingSessionLocal()
    res = process_incoming_report("Is there traffic near Velachery?", "WHATSAPP", db)
    
    assert res["status"] == "FILTERED_NOISE"
    assert res["incident"] is None
    assert db.query(Incident).count() == 0
    # Raw report should still be preserved
    assert db.query(RawReport).count() == 1
    report = db.query(RawReport).first()
    assert report.is_noise is True
    assert report.is_emergency is False
    db.close()

def test_8_conflicting_people_count_detection():
    """TEST 8: Submit two reports with conflicting people counts. -> Expected: CONFLICTING INFORMATION."""
    db = TestingSessionLocal()
    # Initial report with 10 people
    res1 = process_incoming_report("10 people trapped near Velachery MRTS station.", "WHATSAPP", db)
    inc_id = res1["incident"].id
    
    # Conflicting report saying only 4 people trapped
    res2 = process_incoming_report("Only 4 people trapped near Velachery MRTS station.", "SMS", db)
    
    inc = db.query(Incident).filter(Incident.id == inc_id).first()
    conflicts = db.query(IncidentConflict).filter(IncidentConflict.incident_id == inc_id).all()
    
    assert len(conflicts) >= 1
    assert conflicts[0].existing_value == "10"
    assert conflicts[0].conflicting_value == "4"
    assert conflicts[0].status == "PENDING_REVIEW"
    db.close()

def test_9_uncertain_location_handling():
    """TEST 9: Submit an uncertain location. -> Expected: Best-known location + confidence. No false precision."""
    loc_res = parse_location_intelligence("Somewhere near some small tea shop behind the market corner")
    
    assert loc_res["location_confidence"] < 0.60
    assert "Approximate" in loc_res["best_known_location"] or "Pending" in loc_res["best_known_location"]
    assert loc_res["uncertainty_radius_m"] >= 500

def test_10_multi_report_clustering_compression():
    """TEST 10: Submit multiple reports describing the same incident. -> Expected: One evolving incident rather than duplicate tickets."""
    db = TestingSessionLocal()
    reports = [
        "6 people trapped near Velachery MRTS west gate.",
        "Behind the MRTS station on Vijayanagar side, water is waist deep.",
        "Opposite the medical shop near the station backside road, 6 people stuck in house.",
        "Same place near Velachery MRTS west gate, water rising."
    ]
    
    for r in reports:
        process_incoming_report(r, "WHATSAPP", db)
        
    assert db.query(Incident).count() == 1
    inc = db.query(Incident).first()
    assert inc.report_count == 4
    assert inc.verification in ["Verified", "Partially Verified"]
    db.close()

if __name__ == "__main__":
    pytest.main(["-v", __file__])
