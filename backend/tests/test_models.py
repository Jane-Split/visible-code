import pytest
from app.core.database import Base, engine, SessionLocal
from app.models.project import Project
from app.models.entity import Entity
from app.models.graph import Dependency
from app.models.microservice import Microservice, RestEndpoint

def test_database_connection():
    """测试数据库连接"""
    db = SessionLocal()
    try:
        assert db is not None
    finally:
        db.close()

def test_create_tables():
    """测试表创建"""
    Base.metadata.create_all(bind=engine)
    # 验证表已创建
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "projects" in tables
    assert "entities" in tables
    assert "microservices" in tables

def test_project_model():
    """测试 Project 模型"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        project = Project(
            id="test-uuid",
            name="Test Project",
            source_type="git",
            source_url="https://github.com/test/repo.git",
            status="pending"
        )
        db.add(project)
        db.commit()
        
        retrieved = db.query(Project).filter(Project.id == "test-uuid").first()
        assert retrieved is not None
        assert retrieved.name == "Test Project"
        assert retrieved.status == "pending"
    finally:
        db.query(Project).filter(Project.id == "test-uuid").delete()
        db.commit()
        db.close()
