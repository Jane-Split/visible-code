from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(10), nullable=False)  # 'git' or 'local'
    source_url = Column(String(500), nullable=False)
    local_path = Column(String(500))
    default_branch = Column(String(100))
    current_branch = Column(String(100))
    languages = Column(Text)  # JSON array
    last_synced_at = Column(DateTime)
    last_commit_hash = Column(String(40))
    status = Column(String(20), default="pending")  # pending, parsing, ready, error
    config = Column(Text)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    entities = relationship("Entity", back_populates="project", cascade="all, delete-orphan")
    dependencies = relationship("Dependency", back_populates="project", cascade="all, delete-orphan")
    microservices = relationship("Microservice", back_populates="project", cascade="all, delete-orphan")
