from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..utils import crud
from ..schemas import schemas
from ..core.database import get_db
from ..api import deps

router = APIRouter()

@router.post("/", response_model=schemas.EmergencyContact)
def create_contact(
    contact: schemas.EmergencyContactCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    return crud.create_emergency_contact(db=db, contact=contact, user_id=current_user.id)

@router.get("/", response_model=List[schemas.EmergencyContact])
def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    contacts = crud.get_emergency_contacts(db, user_id=current_user.id, skip=skip, limit=limit)
    return contacts

@router.get("/{contact_id}", response_model=schemas.EmergencyContact)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    db_contact = crud.get_emergency_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    if db_contact.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this contact")
    return db_contact

@router.put("/{contact_id}", response_model=schemas.EmergencyContact)
def update_contact(
    contact_id: int,
    contact_update: schemas.EmergencyContactUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    db_contact = crud.get_emergency_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    if db_contact.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this contact")
    return crud.update_emergency_contact(db=db, contact_id=contact_id, contact_update=contact_update)

@router.delete("/{contact_id}", response_model=schemas.EmergencyContact)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    db_contact = crud.get_emergency_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    if db_contact.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this contact")
    return crud.delete_emergency_contact(db=db, contact_id=contact_id)