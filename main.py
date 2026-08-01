from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
from analytics import get_at_risk_students
from attendance_manager import bulk_log_attendance, get_class_attendance_summary

app = FastAPI(
    title="Schoolly Smart Backend API",
    description="REST API for school attendance management, capacity enforcement, and student risk analytics.",
    version="1.0.0"
)

# Pydantic schema for incoming attendance records
class AttendanceRecord(BaseModel):
    student_id: int
    status: str
    date: str

@app.get("/")
def read_root():
    """Health check endpoint to verify backend server status."""
    return {
        "status": "online",
        "system": "Schoolly Smart Engine",
        "docs_url": "/docs"
    }

@app.get("/api/analytics/at-risk")
def fetch_at_risk_students(threshold: float = Query(75.0, ge=0.0, le=100.0)):
    """
    Returns a list of students whose attendance rate falls below the given threshold percentage.
    """
    results = get_at_risk_students(threshold_pct=threshold)
    return {
        "threshold_pct": threshold,
        "count": len(results),
        "students": results
    }

@app.get("/api/attendance/summary/{class_id}")
def fetch_class_summary(class_id: int):
    """
    Retrieves daily attendance metrics (total logged, present, late, absent, attendance rate) for a class.
    """
    summary = get_class_attendance_summary(class_id)
    if not summary:
        raise HTTPException(status_code=404, detail="No attendance logs found for this class.")
    return summary

@app.post("/api/attendance/bulk")
def log_attendance_batch(records: List[AttendanceRecord]):
    """
    Batch logs student attendance status using ON CONFLICT upsert logic.
    """
    # Convert Pydantic models back to tuple format (student_id, status, date)
    formatted_batch = [(r.student_id, r.status, r.date) for r in records]
    
    success = bulk_log_attendance(formatted_batch)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to log bulk attendance records.")
        
    return {
        "status": "success",
        "records_processed": len(records)
    }