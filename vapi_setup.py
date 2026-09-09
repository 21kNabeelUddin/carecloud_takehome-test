import httpx
import os
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")


def create_vapi_assistant():
    """Create a Vapi assistant for patient registration."""
    
    system_prompt = """You are a friendly medical intake coordinator helping patients register at a healthcare facility.

Your job is to collect the following REQUIRED information through natural conversation:
- First name
- Last name  
- Date of birth (MM/DD/YYYY format)
- Sex (Male, Female, Other, or Decline to Answer)
- Phone number (10 digits)
- Street address (address_line_1)
- City
- State (2-letter abbreviation)
- ZIP code

OPTIONAL information (offer after collecting required fields):
- Email
- Apartment/Suite/Unit (address_line_2)
- Insurance provider
- Insurance member ID
- Preferred language
- Emergency contact name
- Emergency contact phone number

IMPORTANT RULES:
1. Be conversational and natural - NOT robotic or scripted.
2. Validate data as you collect it:
   - Phone numbers must be 10 digits
   - Dates must be valid MM/DD/YYYY and not in the future
   - State must be a valid 2-letter US abbreviation
   - ZIP codes must be 5 digits or ZIP+4 format
3. If data is invalid, ask for clarification specifically for that field.
4. Handle corrections gracefully (e.g., "Actually, my last name is spelled D-A-V-I-S").
5. Before saving, read back ALL collected information and ask for confirmation.
6. After confirmation, use the save_patient tool to save the data.
7. Provide a friendly confirmation after saving (e.g., "You're all set, [First Name]!").
8. If the caller wants to start over at any point, restart the conversation.

The conversation should flow naturally like this:
1. Greet the caller warmly
2. Ask for information one piece at a time (or in small groups)
3. Confirm understanding ("Got it, your first name is [Name]")
4. After collecting all required fields, offer optional fields
5. Read back everything for confirmation
6. Save and confirm completion"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "save_patient",
                "description": "Save a new patient record to the database. Call this after collecting all required information and getting caller confirmation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "first_name": {
                            "type": "string",
                            "description": "Patient's first name (1-50 characters, alphabetic with hyphens/apostrophes)"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Patient's last name (1-50 characters, alphabetic with hyphens/apostrophes)"
                        },
                        "date_of_birth": {
                            "type": "string",
                            "description": "Date of birth in MM/DD/YYYY format, must not be in the future"
                        },
                        "sex": {
                            "type": "string",
                            "enum": ["Male", "Female", "Other", "Decline to Answer"],
                            "description": "Patient's sex"
                        },
                        "phone_number": {
                            "type": "string",
                            "description": "10-digit US phone number (digits only)"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address (optional)"
                        },
                        "address_line_1": {
                            "type": "string",
                            "description": "Street address"
                        },
                        "address_line_2": {
                            "type": "string",
                            "description": "Apartment, Suite, or Unit number (optional)"
                        },
                        "city": {
                            "type": "string",
                            "description": "City name (1-100 characters)"
                        },
                        "state": {
                            "type": "string",
                            "description": "2-letter US state abbreviation (e.g., CA, NY, TX)"
                        },
                        "zip_code": {
                            "type": "string",
                            "description": "5-digit or ZIP+4 format ZIP code"
                        },
                        "insurance_provider": {
                            "type": "string",
                            "description": "Name of insurance company (optional)"
                        },
                        "insurance_member_id": {
                            "type": "string",
                            "description": "Insurance member/subscriber ID (optional)"
                        },
                        "preferred_language": {
                            "type": "string",
                            "description": "Preferred language, defaults to English (optional)"
                        },
                        "emergency_contact_name": {
                            "type": "string",
                            "description": "Emergency contact full name (optional)"
                        },
                        "emergency_contact_phone": {
                            "type": "string",
                            "description": "Emergency contact 10-digit phone number (optional)"
                        }
                    },
                    "required": [
                        "first_name", "last_name", "date_of_birth", "sex",
                        "phone_number", "address_line_1", "city", "state", "zip_code"
                    ]
                }
            }
        }
    ]

    assistant_config = {
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.7
        },
        "voice": {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM"
        },
        "firstMessage": "Hello! Thank you for calling. I'm here to help you with your patient registration. I'll walk you through a few questions to get you set up. Let's start with your first name - what is your first name?",
        "systemPrompt": system_prompt,
        "tools": tools,
        "maxDurationSeconds": 300,
        "endCallFunctionEnabled": True
    }

    return assistant_config


def get_webhook_url():
    """Return the webhook URL for Vapi to call."""
    server_url = os.getenv("SERVER_URL", "http://localhost:8000")
    return f"{server_url}/vapi/webhook"


if __name__ == "__main__":
    config = create_vapi_assistant()
    print("Vapi Assistant Configuration:")
    print(f"Webhook URL: {get_webhook_url()}")
    print("\nTo set up Vapi:")
    print("1. Go to https://dashboard.vapi.ai")
    print("2. Create an account and get your API key")
    print("3. Buy a phone number")
    print("4. Create an assistant with the configuration above")
    print("5. Set the webhook URL to:", get_webhook_url())
    print("6. Update your .env file with the VAPI_API_KEY, VAPI_PHONE_NUMBER_ID, and VAPI_ASSISTANT_ID")
