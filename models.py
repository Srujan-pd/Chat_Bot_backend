<<<<<<< HEAD
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)
    answer = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
=======
from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
from datetime import datetime

class Chat(Base):
    __tablename__ = "chats_info"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_id = Column(String(36), index=True, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

>>>>>>> b72a9f6 (backend)
