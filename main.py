from fastapi import FastAPI, HTTPException, Depends
from database import Base, engine, SessionLocal
from models import User, Post
from sqlalchemy.orm import Session
from schemas import UserCreate, UserInDB, PostCreate, PostInDB, PostOutDB
from utils import generate_token
from helper import create_user, create_post
from authentication import verify_token
from typing import List
from cachetools import cached, TTLCache

app = FastAPI()
cache = TTLCache(maxsize=1000, ttl=300)

def create_tables():
    Base.metadata.create_all(bind=engine)
create_tables()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=UserInDB)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Parameters:
    - user (UserCreate): The user data to be registered.
    - db (Session, optional): The database session. If not provided, it will be obtained through the `get_db` dependency.

    Returns:
    - UserInDB: The newly registered user data.

    Raises:
    - HTTPException(400): If the provided email is already registered.
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return create_user(db, user)

@app.post("/login", response_model=UserInDB)
def login(user_credentials: UserCreate, db: Session = Depends(get_db)):
    """
    Log in an existing user.

    Parameters:
    - user_credentials (UserCreate): The user credentials (email and password) for login.
    - db (Session, optional): The database session. If not provided, it will be obtained through the `get_db` dependency.

    Returns:
    - UserInDB: The user data including authentication token upon successful login.

    Raises:
    - HTTPException(401): If the provided email or password is incorrect.
    """
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if user is None or user.password != user_credentials.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = generate_token(user.id)
    user.token = token.decode("utf-8")

    return user

@app.post("/posts", response_model=PostInDB)
def create_post_api(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(verify_token)):
    """
    Create a new post.

    Parameters:
    - post (PostCreate): The data of the post to be created.
    - db (Session, optional): The database session. If not provided, it will be obtained through the `get_db` dependency.
    - current_user (User): The authenticated user obtained from the authentication token.

    Returns:
    - PostInDB: The newly created post data.

    Raises:
    - HTTPException(401): If the authentication token is invalid or expired.
    """
    return create_post(db, post, current_user.id)

@app.get("/posts", response_model=List[PostOutDB])
@cached(cache)
def get_posts_by_owner_id(db: Session = Depends(get_db), current_user: User = Depends(verify_token)):
    """
    Retrieve posts owned by the authenticated user.

    Parameters:
    - db (Session, optional): The database session. If not provided, it will be obtained through the `get_db` dependency.
    - current_user (User): The authenticated user obtained from the authentication token.

    Returns:
    - List[PostOutDB]: A list of posts owned by the authenticated user.

    Raises:
    - HTTPException(401): If the authentication token is invalid or expired.
    """
    posts = db.query(Post).filter(Post.owner_id == current_user.id).all()
    return posts

@app.delete("/posts/{post_id}")
def delete_post_by_id(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(verify_token)):
    """
    Delete a post by its ID, if it belongs to the authenticated user.

    Parameters:
    - post_id (int): The ID of the post to be deleted.
    - db (Session, optional): The database session. If not provided, it will be obtained through the `get_db` dependency.
    - current_user (User): The authenticated user obtained from the authentication token.

    Returns:
    - dict: A message confirming the successful deletion of the post.

    Raises:
    - HTTPException(401): If the authentication token is invalid or expired.
    - HTTPException(404): If the post with the given ID is not found or does not belong to the authenticated user.
    """
    post = db.query(Post).filter(Post.id == post_id, Post.owner_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}