from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    accidents = relationship("Accident", back_populates="user")
    contacts = relationship("EmergencyContact", back_populates="user")

class Accident(Base):
    __tablename__ = "accidents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    acceleration_x = Column(Float, nullable=False)
    acceleration_y = Column(Float, nullable=False)
    acceleration_z = Column(Float, nullable=False)
    gyroscope_x = Column(Float, nullable=False)
    gyroscope_y = Column(Float, nullable=False)
    gyroscope_z = Column(Float, nullable=False)
    speed = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    is_confirmed = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="accidents")
    alerts = relationship("Alert", back_populates="accident")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=True)
    is_primary = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="contacts")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    accident_id = Column(Integer, ForeignKey("accidents.id"), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    alert_type = Column(String, nullable=False)  # SMS, EMAIL, etc.
    recipient = Column(String, nullable=False)  # Phone number or email
    status = Column(String, nullable=False)  # SENT, FAILED, etc.
    message = Column(Text, nullable=True)
    
    # Relationships
    accident = relationship("Accident", back_populates="alerts")