import logging
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

from analytics import get_at_risk_students
from attendance_manager import (
    calculate_attendance_percentage,
    get_student_attendance,
    record_daily_attendance,
)
from db_manager import get_connection

logger = logging.getLogger(__name__)


class RootResponse(BaseModel):
    """Service health information returned by the root endpoint."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "online",
                    "message": "Schoolly Smart API is running",
                }
            ]
        }
    )

    status: str
    message: str


class AtRiskStudent(BaseModel):
    """Attendance metrics for a student below the requested threshold."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "student_id": 1,
                    "name": "Abebe Kebede",
                    "email": "abebe@schoolly.com",
                    "total_days": 20,
                    "days_present": 12,
                    "attendance_rate_pct": 60.0,
                }
            ]
        }
    )

    student_id: int
    name: str
    email: str | None
    total_days: int
    days_present: int
    attendance_rate_pct: float


class AttendanceCreate(BaseModel):
    """Request body for recording one daily attendance status."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "student_id": 1,
                    "attendance_date": "2026-09-02",
                    "status": "Present",
                }
            ]
        }
    )

    student_id: int
    attendance_date: date
    status: str


class AttendanceRecord(BaseModel):
    """One stored attendance record for a student."""

    attendance_id: int
    date: date
    status: str


class AttendancePercentage(BaseModel):
    """Aggregated attendance percentage for a student."""

    student_id: int
    total_days: int
    present_days: int
    attendance_percentage: float


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        connection = get_connection()
        connection.close()
        logger.info("Database startup check succeeded")
    except Exception:
        logger.exception("Database startup check failed; continuing without a database connection")
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_origin_regex=r"https://([a-z0-9-]+\.)?(lovable\.app|lovableproject\.com)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(
    "/",
    response_model=RootResponse,
    status_code=200,
    summary="Check API status",
    description="Returns the current availability status of the Schoolly Smart API.",
    responses={200: {"description": "The API is online."}},
)
def read_root() -> RootResponse:
    """Return a health response confirming that the API is running."""
    return {"status": "online", "message": "Schoolly Smart API is running"}

@app.get(
    "/api/analytics/at-risk",
    response_model=list[AtRiskStudent],
    status_code=200,
    summary="List at-risk students",
    description=(
        "Returns students whose attendance rate is below the supplied percentage "
        "threshold, ordered from lowest attendance rate to highest."
    ),
    responses={200: {"description": "At-risk student attendance metrics."}},
)
def at_risk_students(
    threshold: float = Query(
        75.0,
        ge=0,
        le=100,
        description="Only return students with attendance below this percentage.",
    ),
) -> list[AtRiskStudent]:
    """Return students whose attendance rate is below ``threshold`` percent."""
    return get_at_risk_students(threshold_pct=threshold)


@app.post(
    "/api/attendance",
    response_model=AttendanceRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Record daily attendance",
    description="Record a student's attendance status for a specific calendar date.",
    responses={201: {"description": "Attendance record created."}},
)
def create_attendance_record(
    attendance: AttendanceCreate,
) -> AttendanceRecord:
    """Store one attendance status and return the created record."""
    return record_daily_attendance(
        attendance.student_id,
        attendance.attendance_date,
        attendance.status,
    )


@app.get(
    "/api/attendance/student/{student_id}",
    response_model=list[AttendanceRecord],
    status_code=status.HTTP_200_OK,
    summary="Get student attendance",
    description="Return all recorded attendance entries for an individual student.",
    responses={200: {"description": "The student's attendance records."}},
)
def student_attendance(student_id: int) -> list[AttendanceRecord]:
    """Return an individual student's attendance history."""
    return get_student_attendance(student_id)


@app.get(
    "/api/attendance/student/{student_id}/percentage",
    response_model=AttendancePercentage,
    status_code=status.HTTP_200_OK,
    summary="Calculate attendance percentage",
    description="Calculate the percentage of recorded days marked Present for a student.",
    responses={200: {"description": "The student's attendance percentage."}},
)
def student_attendance_percentage(student_id: int) -> AttendancePercentage:
    """Return the student's attendance percentage over all recorded days."""
    return calculate_attendance_percentage(student_id)
