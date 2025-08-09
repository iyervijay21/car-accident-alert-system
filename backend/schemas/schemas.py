from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Accident schemas
class AccidentBase(BaseModel):
    latitude: float
    longitude: float
    acceleration_x: float
    acceleration_y: float
    acceleration_z: float
    gyroscope_x: float
    gyroscope_y: float
    gyroscope_z: float
    speed: Optional[float] = None

class AccidentCreate(AccidentBase):
    pass

class AccidentUpdate(BaseModel):
    is_confirmed: bool

class AccidentInDBBase(AccidentBase):
    id: int
    user_id: int
    timestamp: datetime
    confidence_score: Optional[float] = None
    is_confirmed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Accident(AccidentInDBBase):
    pass

# Emergency contact schemas
class EmergencyContactBase(BaseModel):
    name: str
    phone_number: str
    email: Optional[EmailStr] = None
    is_primary: bool = False

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactUpdate(EmergencyContactBase):
    pass

class EmergencyContactInDBBase(EmergencyContactBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EmergencyContact(EmergencyContactInDBBase):
    pass

# Alert schemas
class AlertBase(BaseModel):
    alert_type: str
    recipient: str
    status: str
    message: Optional[str] = None

class AlertCreate(AlertBase):
    accident_id: int

class AlertUpdate(BaseModel):
    status: str

class AlertInDBBase(AlertBase):
    id: int
    accident_id: int
    sent_at: datetime

    class Config:
        from_attributes = True

class Alert(AlertInDBBase):
    pass

# ML schemas
class SensorData(BaseModel):
    timestamp: datetime
    acceleration_x: float
    acceleration_y: float
    acceleration_z: float
    gyroscope_x: float
    gyroscope_y: float
    gyroscope_z: float
    speed: Optional[float] = None

class PredictionRequest(BaseModel):
    sensor_data: List[SensorData]

class PredictionResponse(BaseModel):
    is_accident: bool
    confidence: float