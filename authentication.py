from fastapi import exceptions
from models import User
import jwt
from functools import wraps
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
SECRET_KEY = "secret"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_token(token: str, db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('user_id')
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return user
        else:
            raise HTTPException(status_code=401, detail="User not found")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token is invalid")

