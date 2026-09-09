from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: str = Field(..., pattern=r"^\d{2}/\d{2}/\d{4}$")
    sex: str = Field(..., pattern=r"^(Male|Female|Other|Decline to Answer)$")
    phone_number: str = Field(..., pattern=r"^\d{10}$")
    email: Optional[str] = None
    address_line_1: str = Field(..., min_length=1)
    address_line_2: Optional[str] = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., pattern=r"^[A-Z]{2}$")
    zip_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = "English"
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @validator("date_of_birth")
    def validate_dob(cls, v):
        try:
            dob = datetime.strptime(v, "%m/%d/%Y")
            if dob > datetime.now():
                raise ValueError("Date of birth cannot be in the future")
        except ValueError as e:
            raise ValueError(str(e))
        return v


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    date_of_birth: Optional[str] = Field(None, pattern=r"^\d{2}/\d{2}/\d{4}$")
    sex: Optional[str] = Field(None, pattern=r"^(Male|Female|Other|Decline to Answer)$")
    phone_number: Optional[str] = Field(None, pattern=r"^\d{10}$")
    email: Optional[str] = None
    address_line_1: Optional[str] = Field(None, min_length=1)
    address_line_2: Optional[str] = None
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, pattern=r"^[A-Z]{2}$")
    zip_code: Optional[str] = Field(None, pattern=r"^\d{5}(-\d{4})?$")
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class PatientResponse(PatientBase):
    patient_id: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

    class Config:
        from_attributes = True
