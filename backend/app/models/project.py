from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from backend.app.database import Base


class DBProject(Base):
    """Project model for storing video project data."""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_data = Column(LargeBinary, nullable=False)
    
    def __repr__(self):
        return f"DBProject('{self.title}', user_id={self.user_id})"
