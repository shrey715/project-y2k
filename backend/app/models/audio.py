from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import JSON
from backend.app.database import Base


class Audio(Base):
    """Audio model for storing user audio files."""
    
    __tablename__ = "audios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    audio = Column(LargeBinary, nullable=False)  # PostgreSQL BYTEA
    file_metadata = Column("metadata", JSON)
    used_in_projects = Column(Integer, default=0)
    
    def __repr__(self):
        return f"Audio('{self.filename}', user_id={self.user_id})"
