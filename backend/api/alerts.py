from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..utils import crud
from ..schemas import schemas
from ..core.database import get_db
from ..api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Alert)
def create_alert(
    alert: schemas.AlertCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    # Verify the accident belongs to the user
    db_accident = crud.get_accident(db, accident_id=alert.accident_id)
    if db_accident is None:
        raise HTTPException(status_code=404, detail="Accident not found")
    if db_accident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to create alert for this accident")
    
    return crud.create_alert(db=db, alert=alert)

@router.get("/", response_model=List[schemas.Alert])
def read_alerts(
    accident_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    # Verify the accident belongs to the user
    db_accident = crud.get_accident(db, accident_id=accident_id)
    if db_accident is None:
        raise HTTPException(status_code=404, detail="Accident not found")
    if db_accident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access alerts for this accident")
    
    alerts = crud.get_alerts(db, accident_id=accident_id, skip=skip, limit=limit)
    return alerts

@router.get("/{alert_id}", response_model=schemas.Alert)
def read_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    db_alert = crud.get_alert(db, alert_id=alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Verify the accident belongs to the user
    db_accident = crud.get_accident(db, accident_id=db_alert.accident_id)
    if db_accident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this alert")
    
    return db_alert

@router.put("/{alert_id}", response_model=schemas.Alert)
def update_alert(
    alert_id: int,
    alert_update: schemas.AlertUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    db_alert = crud.get_alert(db, alert_id=alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Verify the accident belongs to the user
    db_accident = crud.get_accident(db, accident_id=db_alert.accident_id)
    if db_accident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this alert")
    
    return crud.update_alert(db=db, alert_id=alert_id, alert_update=alert_update)