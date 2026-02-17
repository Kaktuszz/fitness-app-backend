from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, JSON, Date, Enum as SQLALchemyEnum
from sqlalchemy.orm import relationship
from database.db_engine import Base
from database.enums import GenderEnum, ExperienceLevelEnum

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), nullable=False, index=True, unique=True)
    email = Column(String(30), nullable=False, index=True, unique=True)
    password = Column(String)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    gender = Column(SQLALchemyEnum(GenderEnum))
    activity_level = Column(String(20), nullable=True)
    goal_progress = Column(Integer, nullable=True)
    experience = Column(SQLALchemyEnum(ExperienceLevelEnum))
    goal = Column(String(30), nullable=False)
    deadline = Column(DateTime, nullable=True)
    gadget = Column(String)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    healthdata = relationship("HealthData", back_populates="user", cascade="all, delete-orphan")

class Workout(Base):
    __tablename__ = 'workouts'

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(100), nullable=False)
    bpm = Column(JSON, nullable=False)
    hrv = Column(JSON, nullable=False)
    source = Column(String)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    calories_burned = Column(Float)
    distance = Column(Float)
    steps = Column(Integer)
    notes = Column(String)
    created_at = Column(DateTime, nullable=False)


    user = relationship("User", back_populates="workouts")

class HealthData(Base):
    __tablename__ = "health_data"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    in_bed_seconds = Column(Integer)
    asleep_seconds = Column(Integer)
    deep_seconds = Column(Integer)
    core_seconds = Column(Integer)
    rem_seconds = Column(Integer)
    awake_seconds = Column(Integer)
    avg_sleep_bpm = Column(Float)
    temperature_delta = Column(Float)
    steps = Column(Integer)
    activity_minutes = Column(Integer)
    resting_hr = Column(JSON)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    weight_history = Column(JSON)

    user = relationship("User", back_populates="healthdata")

    

