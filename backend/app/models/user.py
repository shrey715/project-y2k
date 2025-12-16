from sqlalchemy import Column, Integer, String
from backend.app.database import Base


class User(Base):
    """User model for storing user information."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(64), nullable=False)  # SHA256 hash
    
    def __repr__(self):
        return f"User({self.id}, '{self.username}', '{self.email}')"
