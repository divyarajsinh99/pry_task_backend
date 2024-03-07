from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserInDB(BaseModel):
    id: int
    email: str
    password: str
    token: str

class PostCreate(BaseModel):
    content: str

class PostInDB(BaseModel):
    id: int

class PostOutDB(BaseModel):
    id: int
    content: str