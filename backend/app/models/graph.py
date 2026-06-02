from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    source_id = Column(String(36), ForeignKey("entities.id"), nullable=False)
    target_id = Column(String(36), ForeignKey("entities.id"), nullable=False)
    type = Column(String(20), nullable=False)  # import, extend, implement, call, reference
    file_path = Column(String(500))
    line = Column(Integer)
    column = Column(Integer)

    # 关系
    project = relationship("Project", back_populates="dependencies")
    source = relationship("Entity", foreign_keys=[source_id])
    target = relationship("Entity", foreign_keys=[target_id])

class CallChain(Base):
    __tablename__ = "call_chains"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    caller_id = Column(String(36), ForeignKey("entities.id"), nullable=False)
    callee_id = Column(String(36), ForeignKey("entities.id"), nullable=False)
    file_path = Column(String(500))
    line = Column(Integer)
    column = Column(Integer)

    # 关系
    caller = relationship("Entity", foreign_keys=[caller_id])
    callee = relationship("Entity", foreign_keys=[callee_id])

class FileIndex(Base):
    __tablename__ = "file_index"

    project_id = Column(String(36), ForeignKey("projects.id"), primary_key=True)
    file_path = Column(String(500), primary_key=True)
    file_hash = Column(String(32), nullable=False)  # MD5
    last_parsed_at = Column(String(30))
