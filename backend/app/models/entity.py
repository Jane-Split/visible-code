from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Entity(Base):
    __tablename__ = "entities"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    type = Column(String(20), nullable=False)  # module, class, interface, function, method, field
    name = Column(String(255), nullable=False)
    qualified_name = Column(String(500), nullable=False)
    parent_id = Column(String(36), ForeignKey("entities.id"))
    start_line = Column(Integer)
    end_line = Column(Integer)
    start_column = Column(Integer)
    end_column = Column(Integer)
    modifiers = Column(Text)  # JSON array
    annotations = Column(Text)  # JSON array
    signature = Column(Text)
    docstring = Column(Text)

    # 关系
    project = relationship("Project", back_populates="entities")
    parent = relationship("Entity", remote_side=[id], backref="children")
