from sqlalchemy.orm import Session
from typing import Optional, List
from ..models import models
from ..schemas import schemas
from ..core.security import get_password_hash, verify_password

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        phone_number=user.phone_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Accident CRUD operations
def get_accident(db: Session, accident_id: int):
    return db.query(models.Accident).filter(models.Accident.id == accident_id).first()

def get_accidents(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Accident).filter(models.Accident.user_id == user_id).offset(skip).limit(limit).all()

def get_all_accidents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Accident).offset(skip).limit(limit).all()

def create_accident(db: Session, accident: schemas.AccidentCreate, user_id: int):
    db_accident = models.Accident(**accident.dict(), user_id=user_id)
    db.add(db_accident)
    db.commit()
    db.refresh(db_accident)
    return db_accident

def update_accident(db: Session, accident_id: int, accident_update: schemas.AccidentUpdate):
    db_accident = db.query(models.Accident).filter(models.Accident.id == accident_id).first()
    if db_accident:
        update_data = accident_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_accident, key, value)
        db.commit()
        db.refresh(db_accident)
    return db_accident

# Emergency contact CRUD operations
def get_emergency_contact(db: Session, contact_id: int):
    return db.query(models.EmergencyContact).filter(models.EmergencyContact.id == contact_id).first()

def get_emergency_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.EmergencyContact).filter(models.EmergencyContact.user_id == user_id).offset(skip).limit(limit).all()

def create_emergency_contact(db: Session, contact: schemas.EmergencyContactCreate, user_id: int):
    db_contact = models.EmergencyContact(**contact.dict(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_emergency_contact(db: Session, contact_id: int, contact_update: schemas.EmergencyContactUpdate):
    db_contact = db.query(models.EmergencyContact).filter(models.EmergencyContact.id == contact_id).first()
    if db_contact:
        update_data = contact_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_emergency_contact(db: Session, contact_id: int):
    db_contact = db.query(models.EmergencyContact).filter(models.EmergencyContact.id == contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

# Alert CRUD operations
def get_alert(db: Session, alert_id: int):
    return db.query(models.Alert).filter(models.Alert.id == alert_id).first()

def get_alerts(db: Session, accident_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Alert).filter(models.Alert.accident_id == accident_id).offset(skip).limit(limit).all()

def create_alert(db: Session, alert: schemas.AlertCreate):
    db_alert = models.Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def update_alert(db: Session, alert_id: int, alert_update: schemas.AlertUpdate):
    db_alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if db_alert:
        update_data = alert_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_alert, key, value)
        db.commit()
        db.refresh(db_alert)
    return db_alert