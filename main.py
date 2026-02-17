from typing import Union, Optional
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.db_engine import SessionLocal, engine
from database.schemas import UserCreate, CreateWorkout, CreateHealthData, WorkoutAnalysis, HealthAnalysis
from auth.auth import create_access_token, get_current_user_id, verify_refresh_token, create_refresh_token
from datetime import timedelta
from auth.security import verify_password
from google import genai

import database.models as models
from crud import users as user_crud
from crud import workouts as workout_crud
from crud import health_data as health_crud
from model_requests.analyze_workout import analyze_workout_data
from model_requests.analyze_health import analyze_health_data


from database.seed_db import seed_data


models.Base.metadata.create_all(bind=engine)



app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#login endpoints

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.id}, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(data={"sub": user.id}, expires_delta=timedelta(days=90))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/refresh-token")
def refresh_access_token(refresh_token: str):
    try:
        user_id = verify_refresh_token(refresh_token)
        # Generate a new access token and refresh token
        access_token = create_access_token(data={"sub": user_id})
        new_refresh_token = create_refresh_token(data={"sub": user_id})
        return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    


###################
# how to protect this endpoint with auth?
@app.get("/user/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/")
def read_all_users(db: Session = Depends(get_db)):
    users = user_crud.get_users(db)
    if users is None:
        raise HTTPException(status_code=404, detail="Users not found")
    return users

@app.post("/user/", response_model=UserCreate)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    db_email = user_crud.user_exists_by_email(db, email=user_data.email)
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_username = user_crud.get_user_by_username(db, username=user_data.username)
    if db_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    return user_crud.create_user(db, user=user_data)


@app.get("/user/workouts")
def read_user_workouts(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    print("Current User ID:", current_user_id)
    return workout_crud.get_workout_by_user(db, user_id=current_user_id)

@app.post("/user/{user_id}/workouts", response_model=CreateWorkout)
def create_user_workout(workout_data: CreateWorkout, db: Session = Depends(get_db)):
    return workout_crud.create_workout(db, workout=workout_data)

# to getting data to send to gemini only from server side
 
@app.get("/user/workouts/recent")
def read_recent_user_workouts(limit: Optional[int] = 14, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return workout_crud.get_recent_workouts_by_user_id(db, user_id=current_user_id, limit=limit)

@app.get("/user/health-data")
def read_user_health(  db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return health_crud.get_user_health_data(db, user_id=current_user_id)

@app.post("/user/{user_id}/health-data", response_model=CreateHealthData)
def create_user_health(health_data: CreateHealthData, db: Session = Depends(get_db)):
    return health_crud.create_health_data(db, health_data=health_data)

@app.get("/user/health-data/recent")
def read_recent_user_health(limit: Optional[int] = 14, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return health_crud.get_recent_health_data_by_user_id(db, user_id=current_user_id, limit=limit)

@app.get("/user/health-data/sleep-quality")
def read_user_sleep_quality(limit: Optional[int] = 14, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return health_crud.get_sleep_quality_by_user_id(db, user_id=current_user_id, limit=limit)

@app.get("/user/health-data/resting_hr-hrv-trends")
def read_user_resting_hr_hrv_trends( db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return health_crud.get_resting_hr_hrv_avg_sleep_bpm_by_user_id(db, user_id=current_user_id)

@app.get("/user/health-data/speps-activity-trends") 
def read_user_steps_activity_trends(limit: Optional[int] = 14, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return health_crud.get_activity_steps_by_user_id(db, user_id=current_user_id, limit=limit)

@app.get("/user/workouts/last-intensity")
def read_user_last_workout_intensity(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return workout_crud.get_last_workout_intensity_by_user_id(db, user_id=current_user_id)

@app.get("/user/workouts/recovery-gap")
def read_user_recovery_gap(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return workout_crud.get_recovery_gap_by_user_id(db, user_id=current_user_id)


# Requests to Gemini API

@app.post("/analyze/workouts-4", response_model=WorkoutAnalysis)
async def get_workout_analysis(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    recent_workouts = workout_crud.get_recent_workouts_by_user_id(
        db, user_id=current_user_id, limit=4
    )

    if not recent_workouts:
        raise HTTPException(status_code=404, detail="No workouts found for this user.")

    result = analyze_workout_data(recent_workouts)

    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    
    return result

@app.post("/analyze/health-4", response_model=HealthAnalysis)
async def get_health_analysis(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    recent_health = health_crud.get_recent_health_data_by_user_id(
        db, user_id=current_user_id, limit=4
    )

    if not recent_health:
        raise HTTPException(status_code=404, detail="No health data found for this user.")

    result = analyze_health_data(recent_health)

    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    
    return result

# seed_data()


# requests to Gemini API

# response = client.models.generate_content(
#     model="gemini-2.5-flash-lite",
#     contents="test, respond: test complete"
# )

# print(response.text)