from utils import generate_token
from models import User, Post
from sqlalchemy.orm import Session
from schemas import UserCreate,PostCreate

def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = generate_token(db_user.id)
    db_user.token = token.decode("utf-8")
    return db_user


def create_post(db: Session, post: PostCreate, current_user_id: int):
    db_post = Post(**post.dict(), owner_id=current_user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post