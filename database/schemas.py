from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from database.enums import GenderEnum, ExperienceLevelEnum
from typing import List

class UserCreate(BaseModel):
    username: str = Field(..., max_length=30, min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: int = Field(..., ge=18)
    weight: float = Field(..., gt=20)
    height: float = Field(..., gt=50)
    gender: GenderEnum 
    activity_level: str
    goal_progress: int = Field(..., ge=0, le=100)
    experience: ExperienceLevelEnum
    goal: str
    deadline: datetime
    gadget: str
    created_at: datetime
    updated_at: datetime

class CreateWorkout(BaseModel):
    workout_id: int = Field(..., ge=0)
    user_id: int = Field(..., ge=0)
    type: str = Field(..., max_length=100)
    bpm: dict
    hrv: dict
    source: str
    start_time: datetime
    end_time: datetime
    calories_burned: float = Field(..., ge=0)
    distance: float = Field(..., ge=0)
    steps: int = Field(..., ge=0)
    notes: str
    created_at: datetime


class CreateHealthData(BaseModel):
    user_id: int = Field(..., ge=0)
    date: datetime
    in_bed_seconds: int = Field(..., ge=0)
    asleep_seconds: int = Field(..., ge=0)
    deep_seconds: int = Field(..., ge=0)
    core_seconds: int = Field(..., ge=0)
    rem_seconds: int = Field(..., ge=0)
    awake_seconds: int = Field(..., ge=0)
    avg_sleep_bpm: float
    temperature_delta: float
    steps: int = Field(..., ge=0)
    activity_minutes: int = Field(..., ge=0)
    resting_hr: dict
    created_at: datetime
    updated_at: datetime
    
    weight_history: dict

class GetRecentHealth(BaseModel):
    user_id: int = Field(..., ge=0)


class WorkoutAnalysis(BaseModel):
    recommendation: str 
    adjustment_reasoning: str # Why they should go harder/easier
    
    # Point 2: Intensity Analysis
    intensity_score: int # 1-10 scale
    intensity_label: str # e.g., "High-Intensity Interval", "Active Recovery"
    
    # Point 3: Additional Insights
    biometric_trends: str
    estimated_recovery_time_hours: int
    suggested_focus: str

class HealthAnalysis(BaseModel):
    sleep_quality_score: int  # 1-10 scale
    sleep_recommendations: str
    resting_hr_trends: str
    activity_level_assessment: str
    suggested_improvements: str

