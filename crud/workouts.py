from sqlalchemy.orm import Session
from database.models import Workout, User
from database.schemas import CreateWorkout
from fastapi import HTTPException
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def get_workout_by_user(db: Session, user_id: int):
    try:
        workouts = db.query(Workout).filter(Workout.user_id == user_id).all()
        return workouts
    except Exception as e:
        logger.error("Error retrieving workouts for user_id %s: %s", user_id, str(e))
        raise HTTPException(status_code=400, detail=str(e))

def get_recent_workouts(db: Session, limit: int = 10):
    try:
        workouts = db.query(Workout).order_by(Workout.start_time.desc()).limit(limit).all()
        return workouts
    except Exception as e:
        logger.error("Error retrieving recent workouts: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))

def create_workout(db: Session, workout: CreateWorkout):
    workout_dict = workout.model_dump()
    new_workout = Workout(**workout_dict)
    try:
        db.add(new_workout)
        db.commit()
        logger.info("User successfully committed to the database.")
        db.refresh(new_workout)
        logger.info("User successfully refreshed: %s", new_workout)
        return new_workout
    except Exception as e:
        db.rollback()
        logger.error("IntegrityError occurred: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
def get_recent_workouts_by_user_id(db: Session, user_id: int, limit: int = 14):
    try:
        workouts = db.query(Workout).filter(Workout.user_id == user_id).order_by(Workout.start_time.desc()).limit(limit).all()
        user_data = db.query(User).filter(User.id == user_id).scalar()
        return {
            "user_goal": user_data.goal if user_data else "General Fitness",
            "user_age": user_data.age if user_data else None,
            "user_weight": user_data.weight if user_data else None,
            "user_height": user_data.height if user_data else None,
            "user_gender": user_data.gender if user_data else None,
            "workouts": workouts
        }
    except Exception as e:
        logger.error("Error retrieving recent workouts for user_id %s: %s", user_id, str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
def get_last_workout_intensity_by_user_id(db: Session, user_id: int):
    try:
        last_workout = db.query(Workout).filter(Workout.user_id == user_id).order_by(Workout.start_time.desc()).first()
        if last_workout:
            intensity = {
                "date": last_workout.created_at,
                "max_bpm": max(last_workout.bpm) if last_workout.bpm else None,
                "avg_bpm": sum(last_workout.bpm) / len(last_workout.bpm) if last_workout.bpm else None,
            }
            return intensity
        else:
            return None
    except Exception as e:
        logger.error("Error retrieving last workout intensity for user_id %s: %s", user_id, str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
def get_recovery_gap_by_user_id(db: Session, user_id: int):
    try:
        last_workout = (
            db.query(Workout)
            .filter(Workout.user_id == user_id)
            .order_by(Workout.end_time.desc())
            .first()
        )

        if last_workout:
            now = datetime.utcnow()
            
            last_end = datetime.fromisoformat(last_workout.end_time)

            recovery_gap = (now - last_end).total_seconds() / 3600.0

            previous_workout = (
                db.query(Workout)
                .filter(
                    Workout.user_id == user_id,
                    Workout.end_time < last_workout.end_time
                )
                .order_by(Workout.end_time.desc())
                .first()
            )

            time_since_previous_workout = None
            if previous_workout:
                prev_end = datetime.fromisoformat(previous_workout.end_time)
                time_since_previous_workout = (
                    (last_end - prev_end).total_seconds() / 3600.0
                )

            return {
                "last_workout_date": last_end,
                "recovery_gap_hours": recovery_gap,
                "time_since_previous_workout_hours": time_since_previous_workout,
                "workout_type": last_workout.type,
            }
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Date error: {str(e)}")