from sqlalchemy.orm import Session
from database.models import User
from fastapi import HTTPException
from sqlalchemy import exists
from database.schemas import UserCreate
from auth.security import get_password_hash
import logging


logger = logging.getLogger(__name__)

# be used for User baseline & goal context in LLM prompts
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def user_exists_by_email(db: Session, email: str) -> bool:
    return db.query(exists().where(User.email == email)).scalar()
    

def get_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, user: UserCreate):
    hashed_pwd = get_password_hash(user.password)
    
    user_data = user.model_dump()
    user_data["password"] = hashed_pwd
    new_user = User(**user_data)
    try:
        db.add(new_user)
        db.commit()
        logger.info("User successfully committed to the database.")
        db.refresh(new_user)
        logger.info("User successfully refreshed: %s", new_user)
        return new_user
    except Exception as e:
        db.rollback()
        logger.error("IntegrityError occurred: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error("An unexpected error occurred: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))

