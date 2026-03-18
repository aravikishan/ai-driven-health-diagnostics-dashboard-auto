from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlite3
import os

# Initialize FastAPI app
app = FastAPI()

# Set up templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE_URL = "./health_diagnostics.db"

# Ensure the database and tables exist
if not os.path.exists(DATABASE_URL):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        gender TEXT NOT NULL
                    )''')
    cursor.execute('''CREATE TABLE diagnostics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER,
                        date TEXT NOT NULL,
                        results TEXT NOT NULL,
                        recommendations TEXT NOT NULL,
                        FOREIGN KEY(patient_id) REFERENCES patients(id)
                    )''')
    # Insert mock data
    cursor.execute("INSERT INTO patients (name, age, gender) VALUES ('John Doe', 30, 'Male')")
    cursor.execute("INSERT INTO diagnostics (patient_id, date, results, recommendations) VALUES (1, '2023-01-01', 'All good', 'Keep a healthy diet')")
    conn.commit()
    conn.close()

# Data models
class Patient(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    diagnostics: List[dict] = []

class Diagnostic(BaseModel):
    id: int
    patient_id: int
    date: datetime
    results: str
    recommendations: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/patients", response_class=HTMLResponse)
async def read_patients(request):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("patients.html", {"request": request, "patients": patients})

@app.get("/patient/{id}", response_class=HTMLResponse)
async def read_patient_detail(request, id: int):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (id,))
    patient = cursor.fetchone()
    cursor.execute("SELECT * FROM diagnostics WHERE patient_id = ?", (id,))
    diagnostics = cursor.fetchall()
    conn.close()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return templates.TemplateResponse("patient_detail.html", {"request": request, "patient": patient, "diagnostics": diagnostics})

@app.get("/analytics", response_class=HTMLResponse)
async def read_analytics(request):
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def read_settings(request):
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/api/patients", response_model=List[Patient])
async def get_patients():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    conn.close()
    return [{"id": p[0], "name": p[1], "age": p[2], "gender": p[3], "diagnostics": []} for p in patients]

@app.get("/api/patient/{id}", response_model=Patient)
async def get_patient(id: int):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (id,))
    patient = cursor.fetchone()
    cursor.execute("SELECT * FROM diagnostics WHERE patient_id = ?", (id,))
    diagnostics = cursor.fetchall()
    conn.close()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"id": patient[0], "name": patient[1], "age": patient[2], "gender": patient[3], "diagnostics": [{"id": d[0], "patient_id": d[1], "date": d[2], "results": d[3], "recommendations": d[4]} for d in diagnostics]}

@app.post("/api/diagnostics", response_model=Diagnostic)
async def create_diagnostic(diagnostic: Diagnostic):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO diagnostics (patient_id, date, results, recommendations) VALUES (?, ?, ?, ?)", (diagnostic.patient_id, diagnostic.date, diagnostic.results, diagnostic.recommendations))
    conn.commit()
    diagnostic_id = cursor.lastrowid
    conn.close()
    return {"id": diagnostic_id, **diagnostic.dict()}

@app.get("/api/analytics")
async def get_analytics():
    # Placeholder for AI-driven analytics
    return {"message": "Predictive analytics data"}
