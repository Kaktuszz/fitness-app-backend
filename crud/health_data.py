from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from database.models import HealthData, Workout, User
from database.schemas import CreateHealthData
from fastapi import HTTPException
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def get_user_health_data(db: Session, user_id: int):
    try:
        health_data = db.query(HealthData).filter(HealthData.user_id == user_id).all()
        return health_data
    except Exception as e:
        logger.error("Error retrieving health data for user_id %s: %s", user_id, str(e))
        raise HTTPException(status_code=400, detail=str(e))

def get_recent_health_data(db: Session, limit: int):
    try:
        health_data = db.query(HealthData).order_by(HealthData.date.desc()).limit(limit).all()
        return health_data
    except Exception as e:
        logger.error("Error retrieving recent health data: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))

def create_health_data(db: Session, health_data: CreateHealthData):
    health_data_dict = health_data.model_dump()
    new_health_data = HealthData(**health_data_dict)
    try:
        db.add(new_health_data)
        db.commit()
        logger.info("Health data successfully committed to the database.")
        db.refresh(new_health_data)
        logger.info("Health data successfully refreshed: %s", new_health_data)
        return new_health_data
    except Exception as e:
        db.rollback()
        logger.error("IntegrityError occurred: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))

# to analyze Daily health & recovery metrics
def get_recent_health_data_by_user_id(db: Session, user_id: int, limit: int):
    try:
        health_data = db.query(HealthData).filter(HealthData.user_id == user_id).order_by(HealthData.date.desc()).limit(limit).all()
        user_data = db.query(User).filter(User.id == user_id).scalar()
        return {
            "user_age": user_data.age if user_data else None,
            "user_weight": user_data.weight if user_data else None,
            "user_height": user_data.height if user_data else None,
            "user_gender": user_data.gender if user_data else None,
            "user_health_data": health_data
            }
    except Exception as e:
        logger.error("Error retrieving recent health data for user_id %s: %s", user_id, str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
# to analyze sleep quality metrics
def get_sleep_quality_by_user_id(db: Session, user_id: int, limit: int = 14):
    try:
        sleep_data = db.query(HealthData.date,
                              HealthData.asleep_seconds,
                              HealthData.deep_seconds,
                              HealthData.core_seconds,
                              HealthData.rem_seconds).filter(HealthData.user_id == user_id).order_by(HealthData.date.desc()).limit(limit).all()
        return sleep_data
    except Exception as e:
        logger.error("Error retrieving sleep quality data for user_id %s: %s", user_id, str(e))
        raise HTTPException(status_code=400, detail=str(e))


#to analyze resting HR & HRV trend comparison
def get_resting_hr_hrv_avg_sleep_bpm_by_user_id(db: Session, user_id: int):
    today = datetime.utcnow().date()
    previous_date = today - timedelta(days=1)

    health_data = (
        db.query(HealthData)
        .filter(
            HealthData.user_id == user_id,
            func.date(HealthData.date) == previous_date
        )
        .order_by(HealthData.date.desc())
        .first()
    )

    workout_hrv = (
        db.query(Workout)
        .filter(
            Workout.user_id == user_id,
            Workout.start_time <= previous_date + timedelta(days=1)
        )
        .order_by(func.abs(func.date(Workout.start_time) - previous_date))
        .first()
    )

    if health_data and workout_hrv:
        return {
            "date": health_data.date,
            "resting_hr": health_data.resting_hr,
            "avg_sleep_bpm": health_data.avg_sleep_bpm,
            "hrv": workout_hrv.hrv,
        }
    else:
        return None
    
def get_activity_steps_by_user_id(db: Session, user_id: int, limit: int = 14):
    try:
        activity_data = db.query(HealthData.date,
                                 HealthData.steps,
                                 HealthData.activity_minutes).filter(HealthData.user_id == user_id).order_by(HealthData.date.desc()).limit(limit).all()
        return activity_data
    except Exception as e:
        logger.error("Error retrieving activity and steps data for user_id %s: %s", user_id, str(e))
        raise HTTPException(status_code=400, detail=str(e))
