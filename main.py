from fastapi import FastAPI
from dotenv import load_dotenv
from analytics import get_at_risk_students

load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "online", "message": "Schoolly Smart API is running"}

@app.get("/api/analytics/at-risk")
def at_risk_students(threshold: float = 75.0):
    return get_at_risk_students(threshold_pct=threshold)