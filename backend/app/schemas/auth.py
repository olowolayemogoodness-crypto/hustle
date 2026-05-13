from pydantic import BaseModel, field_validator
import re

class OTPSendRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_nigerian_phone(cls, v: str) -> str:
        # Normalise to +234XXXXXXXXXX
        v = v.strip().replace(" ", "").replace("-", "")
        if v.startswith("0") and len(v) == 11:
            v = "+234" + v[1:]
        if v.startswith("234") and not v.startswith("+"):
            v = "+" + v
        pattern = r"^\+234[789][01]\d{8}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid Nigerian phone number")
        return v

class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP must be 6 digits")
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int        # seconds
    user: "UserInToken"

class UserInToken(BaseModel):
    id: str
    phone: str
    role: str | None
    kyc_status: str
    is_new_user: bool

class RoleSetRequest(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("worker", "employer"):
            raise ValueError("role must be worker or employer")
        return v

class KYCSubmitRequest(BaseModel):
    nin: str

    @field_validator("nin")
    @classmethod
    def validate_nin(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() or len(v) != 11:
            raise ValueError("NIN must be 11 digits")
        return v