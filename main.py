from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional
from dotenv import load_dotenv
import os
import logging

from models import PatientCreate, PatientUpdate
from database import (
    init_db, create_patient, get_patient, get_patient_by_phone,
    list_patients, update_patient, soft_delete_patient
)
from vapi_webhook import router as vapi_router

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Patient Registration API", lifespan=lifespan)
app.include_router(vapi_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"data": None, "error": "Internal server error"}
    )


def success_response(data, status_code=200):
    return JSONResponse(status_code=status_code, content={"data": data, "error": None})


def error_response(message, status_code=400):
    return JSONResponse(status_code=status_code, content={"data": None, "error": message})


@app.get("/patients")
def list_all_patients(
    last_name: Optional[str] = Query(None),
    date_of_birth: Optional[str] = Query(None),
    phone_number: Optional[str] = Query(None)
):
    patients = list_patients(last_name, date_of_birth, phone_number)
    return success_response(patients)


@app.get("/patients/{patient_id}")
def get_single_patient(patient_id: str):
    patient = get_patient(patient_id)
    if not patient:
        return error_response("Patient not found", 404)
    return success_response(patient)


@app.post("/patients", status_code=201)
def create_new_patient(patient: PatientCreate):
    data = patient.dict()
    existing = get_patient_by_phone(data["phone_number"])
    if existing:
        return error_response(
            f"Patient with phone {data['phone_number']} already exists (ID: {existing['patient_id']})",
            409
        )
    created = create_patient(data)
    return success_response(created, 201)


@app.put("/patients/{patient_id}")
def update_existing_patient(patient_id: str, patient: PatientUpdate):
    data = patient.dict(exclude_unset=True)
    updated = update_patient(patient_id, data)
    if not updated:
        return error_response("Patient not found", 404)
    return success_response(updated)


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: str):
    deleted = soft_delete_patient(patient_id)
    if not deleted:
        return error_response("Patient not found", 404)
    return success_response({"message": "Patient soft-deleted"})


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    try:
        with open("templates/dashboard.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return error_response("Dashboard not available", 404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
