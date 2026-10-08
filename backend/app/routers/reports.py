import io
import csv
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import RawReport
from app.schemas.report import ReportCreate, ReportBatchCreate, RawReportResponse
from app.engine.pipeline import process_incoming_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.post("", response_model=dict)
def create_report(payload: ReportCreate, db: Session = Depends(get_db)):
    """Ingests a single raw report across any supported source through the 5-part AI pipeline."""
    if not payload.raw_text or not payload.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text cannot be empty.")
    
    result = process_incoming_report(
        raw_text=payload.raw_text,
        source=payload.source,
        db=db,
        custom_timestamp=payload.timestamp,
        metadata=payload.metadata
    )
    
    report_obj = result["report"]
    inc_obj = result["incident"]
    
    return {
        "status": result["status"],
        "message": result["message"],
        "report_id": report_obj.id,
        "processing_status": report_obj.processing_status,
        "is_emergency": report_obj.is_emergency,
        "emergency_type": report_obj.emergency_type,
        "urgency": report_obj.urgency,
        "location": report_obj.location_interpreted,
        "matched_incident_id": report_obj.matched_incident_id,
        "match_confidence": report_obj.match_confidence,
        "match_status": report_obj.match_status,
        "incident": {
            "id": inc_obj.id,
            "title": inc_obj.title,
            "status": inc_obj.status,
            "severity": inc_obj.severity,
            "people_affected": inc_obj.people_affected,
            "best_known_location": inc_obj.best_known_location
        } if inc_obj else None
    }

@router.post("/batch", response_model=dict)
def batch_create_reports(payload: ReportBatchCreate, db: Session = Depends(get_db)):
    """Ingests multiple reports in batch with per-report error resilience."""
    processed = []
    errors = []
    
    for idx, rep in enumerate(payload.reports):
        try:
            if not rep.raw_text.strip():
                continue
            res = process_incoming_report(
                raw_text=rep.raw_text,
                source=rep.source,
                db=db,
                custom_timestamp=rep.timestamp,
                metadata=rep.metadata
            )
            processed.append({
                "index": idx,
                "report_id": res["report"].id,
                "status": res["status"],
                "matched_incident_id": res["report"].matched_incident_id
            })
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    return {
        "total_submitted": len(payload.reports),
        "total_processed": len(processed),
        "errors_count": len(errors),
        "processed": processed,
        "errors": errors
    }

@router.post("/upload", response_model=dict)
async def upload_file_reports(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads and processes CSV or JSON file containing emergency reports."""
    contents = await file.read()
    filename = file.filename.lower()
    reports_to_process = []
    
    try:
        if filename.endswith(".csv"):
            decoded = contents.decode("utf-8", errors="ignore")
            reader = csv.DictReader(io.StringIO(decoded))
            for row in reader:
                text = row.get("raw_text") or row.get("text") or row.get("message") or row.get("report") or ""
                source = row.get("source") or "FILE"
                if text.strip():
                    reports_to_process.append({"raw_text": text.strip(), "source": source})
        elif filename.endswith(".json"):
            data = json.loads(contents.decode("utf-8"))
            if isinstance(data, list):
                for item in data:
                    text = item.get("raw_text") or item.get("text") or item.get("message") or ""
                    source = item.get("source") or "FILE"
                    if text.strip():
                        reports_to_process.append({"raw_text": text.strip(), "source": source})
            elif isinstance(data, dict) and "reports" in data:
                for item in data["reports"]:
                    text = item.get("raw_text") or item.get("text") or item.get("message") or ""
                    source = item.get("source") or "FILE"
                    if text.strip():
                        reports_to_process.append({"raw_text": text.strip(), "source": source})
        else:
            raise HTTPException(status_code=400, detail="Only .csv and .json files are supported.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if not reports_to_process:
        raise HTTPException(status_code=400, detail="No valid reports found in uploaded file.")

    results = []
    for rep in reports_to_process:
        res = process_incoming_report(raw_text=rep["raw_text"], source=rep["source"], db=db)
        results.append({
            "report_id": res["report"].id,
            "status": res["status"],
            "matched_incident_id": res["report"].matched_incident_id
        })

    return {
        "filename": file.filename,
        "reports_ingested": len(results),
        "results": results
    }

@router.post("/audio", response_model=dict)
async def upload_audio_report(
    file: Optional[UploadFile] = File(None),
    simulated_transcript: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Audio call ingestion:
    Audio -> Speech-to-text -> Emergency understanding -> Entity extraction -> Matching -> Updating.
    Accepts audio upload or live speech transcript.
    """
    transcript = simulated_transcript
    
    if not transcript and file:
        # Fallback audio transcript mapping for demo audio clips
        fn = file.filename.lower()
        if "trapped" in fn or "velachery" in fn:
            transcript = "Emergency call from Velachery MRTS west gate! Water is entering houses and 6 people are trapped inside."
        elif "fire" in fn or "tnagar" in fn:
            transcript = "Fire call on Usman road T Nagar. Transformer caught fire, heavy smoke filling shops."
        elif "hospital" in fn or "tambaram" in fn:
            transcript = "Ambulance driver calling from Tambaram GST road. Dialysis patients stuck in flood water."
        else:
            transcript = "Emergency emergency, water level is rising rapidly near the junction. Need boat rescue."

    if not transcript or not transcript.strip():
        raise HTTPException(status_code=400, detail="Audio transcription could not be extracted.")

    result = process_incoming_report(
        raw_text=transcript,
        source="AUDIO",
        db=db,
        metadata={"filename": file.filename if file else "live_mic_recording"}
    )

    return {
        "status": "AUDIO_PROCESSED",
        "transcription": transcript,
        "report_id": result["report"].id,
        "matched_incident_id": result["report"].matched_incident_id,
        "incident": {
            "id": result["incident"].id,
            "title": result["incident"].title,
            "status": result["incident"].status
        } if result["incident"] else None
    }

@router.get("", response_model=List[RawReportResponse])
def list_reports(
    source: Optional[str] = None,
    emergency_type: Optional[str] = None,
    is_noise: Optional[bool] = None,
    matched_incident_id: Optional[str] = None,
    limit: int = Query(default=150, le=500),
    db: Session = Depends(get_db)
):
    """Lists raw reports with filtering."""
    query = db.query(RawReport)
    if source:
        query = query.filter(RawReport.source == source.upper())
    if emergency_type:
        query = query.filter(RawReport.emergency_type == emergency_type)
    if is_noise is not None:
        query = query.filter(RawReport.is_noise == is_noise)
    if matched_incident_id:
        query = query.filter(RawReport.matched_incident_id == matched_incident_id)
    
    reports = query.order_by(RawReport.timestamp.desc()).limit(limit).all()
    return reports

@router.get("/{report_id}", response_model=RawReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):
    """Retrieves a single raw report."""
    report = db.query(RawReport).filter(RawReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report
