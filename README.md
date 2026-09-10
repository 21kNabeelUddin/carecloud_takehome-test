# Voice AI Patient Registration System

A voice-based AI agent that collects patient demographic information through natural conversation, persists data to SQLite, and exposes it through a REST API.


## Deployed URLs

- **API**: https://carecloud-patient-api-4dej.onrender.com
- **Dashboard**: https://carecloud-patient-api-4dej.onrender.com/dashboard
- **Phone**: +1 (681) 622 3116



## Known Issue: Voice Call Stability

The Vapi voice agent experiences dropped calls after 15-20 seconds. This is caused by instability in Vapi's WebRTC transport (Daily.co) used by the Dashboard Test Call feature, not by the application code. The issue persists even with a US VPN, pointing to a transport-layer problem on Vapi's side. The assistant config, system prompt, webhook handling, and data persistence are all working correctly — partial call logs show the bot greeting the caller, collecting a first name, and responding before the connection drops.

## Architecture

```
Phone Call (Caller)
       ↓
Voice AI Agent (Vapi + LLM)
       ↓
FastAPI Backend (REST API)
       ↓
SQLite Database (Persistent)
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Telephony + Voice AI | Vapi |
| LLM | GPT-4o (via Vapi) |
| Backend | FastAPI (Python) |
| Database | SQLite |

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

Required variables:
- `VAPI_API_KEY` - Get from https://dashboard.vapi.ai
- `VAPI_PHONE_NUMBER_ID` - Your Vapi phone number ID
- `VAPI_ASSISTANT_ID` - Your Vapi assistant ID
- `SERVER_URL` - Your server URL (use ngrok for local development)

### 3. Set Up Vapi

1. Create account at https://dashboard.vapi.ai
2. Get your API key from Settings
3. Buy a phone number (or use trial credit)
4. Create an assistant with the configuration from `vapi_setup.py`
5. Set the webhook URL to `https://your-server.com/vapi/webhook`

### 4. Start the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. For Local Development (with ngrok)

```bash
ngrok http 8000
```

Use the ngrok URL as your `SERVER_URL` in `.env`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/patients` | List all patients (supports `?last_name=`, `?date_of_birth=`, `?phone_number=`) |
| GET | `/patients/{id}` | Get patient by ID |
| POST | `/patients` | Create new patient |
| PUT | `/patients/{id}` | Update patient |
| DELETE | `/patients/{id}` | Soft-delete patient |
| GET | `/health` | Health check |
| GET | `/dashboard` | Web dashboard for patient records |

## Data Model

### Required Fields
- `first_name` - 1-50 chars, alphabetic + hyphens/apostrophes
- `last_name` - 1-50 chars, alphabetic + hyphens/apostrophes
- `date_of_birth` - MM/DD/YYYY format, not in future
- `sex` - Male, Female, Other, or Decline to Answer
- `phone_number` - 10-digit US phone number
- `address_line_1` - Street address
- `city` - 1-100 characters
- `state` - 2-letter US state abbreviation
- `zip_code` - 5-digit or ZIP+4 format

### Optional Fields
- `email`, `address_line_2`, `insurance_provider`, `insurance_member_id`
- `preferred_language`, `emergency_contact_name`, `emergency_contact_phone`

## Example API Calls

### Create Patient
```bash
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Doe",
    "date_of_birth": "01/15/1990",
    "sex": "Female",
    "phone_number": "5551234567",
    "address_line_1": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "zip_code": "62701"
  }'
```

### List Patients
```bash
curl http://localhost:8000/patients
```

### Get Patient by ID
```bash
curl http://localhost:8000/patients/{patient_id}
```

## Known Limitations

1. **No authentication** - API is open for demonstration purposes
2. **SQLite only** - Not suitable for production multi-server deployments
3. **Vapi requires公网 access** - Use ngrok for local development
4. **No HIPAA compliance** - This is a technical assessment, not production healthcare

## Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
python -m pytest test_api.py -v
```

Tests cover:
- Health check endpoint
- Patient CRUD operations
- Duplicate patient detection
- Vapi webhook handler
- Patient filtering



## Next Steps (If More Time)

1. ~~Add automated tests~~ ✅
2. ~~Web dashboard for patient records~~ ✅
3. Add API authentication (JWT tokens)
4. Implement PostgreSQL for production
5. Add appointment scheduling
6. Multi-language support
7. Call transcript storage
