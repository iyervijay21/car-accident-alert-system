from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..utils import crud
from ..schemas import schemas
from ..core.database import get_db
from ..api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Accident)
def create_accident(
    accident: schemas.AccidentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    return crud.create_accident(db=db, accident=accident, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Accident])
def read_accidents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    accidents = crud.get_accidents(db, user_id=current_user.id, skip=skip, limit=limit)
    return accidents

@router.get("/{accident_id}", response_model=schemas.Accident)
def read_accident(
    accident_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    db_accident = crud.get_accident(db, accident_id=accident_id)
    if db_accident is None:
        raise HTTPException(status_code=404, detail="Accident not found")
    if db_accident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this accident")
    return db_accident

@router.put("/{accident_id}", response_model=schemas.Accident)
def update_accident(
    accident_id: int,
    accident_update: schemas.AccidentUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    db_accident = crud.get_accident(db, accident_id=accident_id)
    if db_accident is None:
        raise HTTPException(status_code=404, detail="Accident not found")
    if db_accident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this accident")
    return crud.update_accident(db=db, accident_id=accident_id, accident_update=accident_update)