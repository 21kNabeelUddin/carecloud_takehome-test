import pytest
from fastapi.testclient import TestClient
from main import app
from database import init_db, get_db
import os

client = TestClient(app)

TEST_PATIENT = {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "01/15/1990",
    "sex": "Male",
    "phone_number": "1234567890",
    "email": "john.doe@email.com",
    "address_line_1": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "zip_code": "62701"
}


def setup_function():
    if os.path.exists("patients.db"):
        os.remove("patients.db")
    init_db()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_patient():
    response = client.post("/patients", json=TEST_PATIENT)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["phone_number"] == "1234567890"
    assert "patient_id" in data


def test_create_duplicate_patient():
    client.post("/patients", json=TEST_PATIENT)
    response = client.post("/patients", json=TEST_PATIENT)
    assert response.status_code == 409
    assert "already exists" in response.json()["error"]


def test_get_patient():
    create_resp = client.post("/patients", json=TEST_PATIENT)
    patient_id = create_resp.json()["data"]["patient_id"]
    
    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    assert response.json()["data"]["first_name"] == "John"


def test_get_nonexistent_patient():
    response = client.get("/patients/nonexistent-id")
    assert response.status_code == 404


def test_list_patients():
    client.post("/patients", json=TEST_PATIENT)
    response = client.get("/patients")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


def test_list_patients_with_filter():
    client.post("/patients", json=TEST_PATIENT)
    response = client.get("/patients?last_name=Doe")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


def test_update_patient():
    create_resp = client.post("/patients", json=TEST_PATIENT)
    patient_id = create_resp.json()["data"]["patient_id"]
    
    update_data = {"email": "newemail@test.com"}
    response = client.put(f"/patients/{patient_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "newemail@test.com"


def test_delete_patient():
    create_resp = client.post("/patients", json=TEST_PATIENT)
    patient_id = create_resp.json()["data"]["patient_id"]
    
    response = client.delete(f"/patients/{patient_id}")
    assert response.status_code == 200
    
    get_resp = client.get(f"/patients/{patient_id}")
    assert get_resp.status_code == 404


def test_vapi_webhook_save_patient():
    payload = {
        "message": {
            "type": "function-call",
            "functionCall": {
                "name": "save_patient",
                "arguments": TEST_PATIENT
            }
        }
    }
    response = client.post("/vapi/webhook", json=payload)
    assert response.status_code == 200
    assert "Patient registered successfully" in response.json()["result"]
