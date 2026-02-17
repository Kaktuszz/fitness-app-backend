from datetime import datetime, timedelta
import random
from database.db_engine import SessionLocal
import database.models as models

def seed_data():
    db = SessionLocal()
    user_id = 1
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        print(f"User {user_id} not found.")
        return

    # Cleanup existing data
    db.query(models.Workout).filter(models.Workout.user_id == user_id).delete()
    db.query(models.HealthData).filter(models.HealthData.user_id == user_id).delete()

    workouts_to_add = []
    health_data_to_add = []
    base_date = datetime.utcnow() - timedelta(days=40)

    for i in range(40):
        current_date = base_date + timedelta(days=i)
        
        # HealthData
        total_sleep = random.randint(24000, 32000)
        daily_health = models.HealthData(
            user_id=user_id,
            date=current_date.date(),
            in_bed_seconds=total_sleep + 2000,
            asleep_seconds=total_sleep,
            deep_seconds=int(total_sleep * 0.15),
            core_seconds=int(total_sleep * 0.60),
            rem_seconds=int(total_sleep * 0.20),
            awake_seconds=2000,
            avg_sleep_bpm=float(random.randint(55, 65)),
            temperature_delta=round(random.uniform(-0.5, 0.5), 2),
            steps=random.randint(3000, 12000),
            activity_minutes=random.randint(20, 100),
            resting_hr={"avg": random.randint(58, 66)},
            weight_history={"weight": 80.0 - (i * 0.1)},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        health_data_to_add.append(daily_health)

        # Workouts
        if random.random() > 0.4:
            workout_start = current_date.replace(hour=18, minute=0, second=0, microsecond=0)
            workout_end = workout_start + timedelta(minutes=45)

            new_workout = models.Workout(
                workout_id=random.randint(100000, 999999),
                user_id=user_id,
                type=random.choice(["Running", "Strength", "HIIT"]),
                bpm={"avg": 145},
                hrv={"avg": 45},
                source="Apple Watch",
                # REMOVED .isoformat() -> Passing actual datetime objects now
                start_time=workout_start, 
                end_time=workout_end,
                calories_burned=float(random.randint(300, 600)),
                distance=5.2 if i % 2 == 0 else 0.0,
                steps=random.randint(4000, 7000),
                notes="Seed data",
                created_at=datetime.utcnow()
            )
            workouts_to_add.append(new_workout)

    try:
        db.add_all(health_data_to_add)
        db.add_all(workouts_to_add)
        db.commit()
        print(f"✅ Data seeded successfully for user {user_id}!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()