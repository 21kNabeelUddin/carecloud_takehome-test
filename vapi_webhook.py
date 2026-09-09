from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import json

from database import create_patient, get_patient_by_phone

router = APIRouter()


def log_message(msg_type, data):
    """Log incoming Vapi messages."""
    timestamp = datetime.utcnow().isoformat()
    print(f"[{timestamp}] VAPI {msg_type}: {json.dumps(data, indent=2, default=str)}")


@router.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    """Handle incoming webhook calls from Vapi."""
    body = await request.json()
    
    message = body.get("message", {})
    msg_type = message.get("type", "unknown")
    
    log_message(msg_type, body)
    
    # Handle function/tool calls
    if msg_type == "function-call" or message.get("functionCall"):
        function_call = message.get("functionCall", {})
        tool_name = function_call.get("name")
        args = function_call.get("arguments", {})
        
        if tool_name == "save_patient":
            return await handle_save_patient(args)
    
    # For all other message types, return empty object
    return JSONResponse(status_code=200, content={})


async def handle_save_patient(args):
    """Handle saving a patient record."""
    phone = args.get("phone_number")
    
    # Check for existing patient
    existing = get_patient_by_phone(phone) if phone else None
    if existing:
        return JSONResponse(
            status_code=200,
            content={
                "result": f"Patient already exists with this phone number. Patient ID: {existing['patient_id']}. Would you like to update the existing record instead?"
            }
        )
    
    try:
        patient = create_patient(args)
        log_message("PATIENT_CREATED", patient)
        return JSONResponse(
            status_code=200,
            content={
                "result": f"Patient registered successfully! Patient ID: {patient['patient_id']}. You're all set, {args.get('first_name')}!"
            }
        )
    except Exception as e:
        log_message("ERROR", {"error": str(e)})
        return JSONResponse(
            status_code=200,
            content={
                "result": f"I'm sorry, there was an error saving your information. Please try again."
            }
        )


@router.post("/vapi/tool-callback")
async def vapi_tool_callback(request: Request):
    """Handle tool call callbacks from Vapi."""
    body = await request.json()
    log_message("TOOL_CALLBACK", body)
    
    tool_name = body.get("toolName")
    arguments = body.get("arguments", {})
    
    if tool_name == "save_patient":
        return await handle_save_patient(arguments)
    
    return JSONResponse(status_code=200, content={"result": "OK"})
