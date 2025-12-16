from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import JSON
from backend.app.database import Base


class Image(Base):
    """Image model for storing user images."""
    
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image = Column(LargeBinary, nullable=False)  # PostgreSQL BYTEA
    file_metadata = Column("metadata", JSON)
    used_in_projects = Column(Integer, default=0)
    
    def __repr__(self):
        return f"Image('{self.filename}', user_id={self.user_id})"
