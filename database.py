from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "mysql://root:123456@localhost/task_db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

Base=declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
