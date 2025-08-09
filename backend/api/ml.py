from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import numpy as np
from ..utils import crud
from ..schemas import schemas
from ..core.database import get_db
from ..api import deps
from ..ml.model import load_model, preprocess_sensor_data
from ..utils.alerts import send_alerts

router = APIRouter()

# Global model variable (in production, you might want to use a more robust solution)
model = None

@router.on_event("startup")
async def load_model_on_startup():
    global model
    model = load_model("accident_detection_model.h5")
    if model is None:
        print("Warning: Could not load accident detection model")

@router.post("/predict", response_model=schemas.PredictionResponse)
def predict_accident(
    request: schemas.PredictionRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    global model
    
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Preprocess sensor data
        sensor_data = [data.dict() for data in request.sensor_data]
        processed_data = preprocess_sensor_data(sensor_data)
        
        # Make prediction
        prediction = model.predict(processed_data)
        confidence = float(prediction[0][0])
        is_accident = confidence > 0.5
        
        # If it's an accident, trigger alerts
        if is_accident:
            # Get user's emergency contacts
            contacts = crud.get_emergency_contacts(db, user_id=current_user.id)
            contact_dicts = [
                {
                    "id": contact.id,
                    "name": contact.name,
                    "phone_number": contact.phone_number,
                    "email": contact.email
                }
                for contact in contacts
            ]
            
            # Get latest sensor data point for location
            latest_data = sensor_data[-1] if sensor_data else {}
            accident_info = {
                "location": f"Lat: {latest_data.get('latitude', 'N/A')}, Lon: {latest_data.get('longitude', 'N/A')}",
                "confidence": confidence,
                "time": latest_data.get('timestamp', 'N/A')
            }
            
            # Send alerts
            alert_results = send_alerts(contact_dicts, accident_info)
            
            # Save accident to database
            if sensor_data:
                accident_create = schemas.AccidentCreate(
                    latitude=latest_data.get('latitude', 0),
                    longitude=latest_data.get('longitude', 0),
                    acceleration_x=latest_data.get('acceleration_x', 0),
                    acceleration_y=latest_data.get('acceleration_y', 0),
                    acceleration_z=latest_data.get('acceleration_z', 0),
                    gyroscope_x=latest_data.get('gyroscope_x', 0),
                    gyroscope_y=latest_data.get('gyroscope_y', 0),
                    gyroscope_z=latest_data.get('gyroscope_z', 0),
                    speed=latest_data.get('speed'),
                    confidence_score=confidence
                )
                accident = crud.create_accident(db, accident_create, current_user.id)
                
                # Save alerts to database
                for result in alert_results:
                    alert_create = schemas.AlertCreate(
                        accident_id=accident.id,
                        alert_type=result["type"],
                        recipient=result["recipient"],
                        status="SENT" if result["success"] else "FAILED",
                        message=f"Accident alert with {confidence*100:.1f}% confidence"
                    )
                    crud.create_alert(db, alert_create)
        
        return schemas.PredictionResponse(
            is_accident=is_accident,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/retrain")
def retrain_model(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user)
):
    # In a real implementation, you would:
    # 1. Collect new labeled data from the database
    # 2. Retrain the model
    # 3. Save the new model
    # 4. Reload the model in memory
    
    # This is a placeholder implementation
    return {"message": "Model retraining initiated"}