from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pytz

# Load environment variables from .env file
load_dotenv()

SUPABASE_DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL')

if not SUPABASE_DATABASE_URL:
    raise ValueError("SUPABASE_DATABASE_URL is not set in the environment.")

engine = create_engine(SUPABASE_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

def get_utc_plus_3_time():
    utc_plus_3 = pytz.timezone('Etc/GMT-3')
    return datetime.now(utc_plus_3)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    timestamps= Column(DateTime, default=get_utc_plus_3_time())
    messages = relationship("UserMessage", back_populates="user")

class UserMessage(Base):
    __tablename__ = 'user_messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    username = Column(Text, nullable=False)
    message_text = Column(Text, nullable=False)
    timestamps= Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="messages")

Base.metadata.create_all(engine)
