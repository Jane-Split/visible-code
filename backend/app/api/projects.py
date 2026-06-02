from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.git import GitOperator, GitOperationError
from app.core.config import REPOS_PATH
from app.models.project import Project

router = APIRouter(prefix="/api/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    source_type: str  # 'git' or 'local'
    source_url: str
    branch: Optional[str] = "main"
    config: Optional[dict] = {}

class ProjectResponse(BaseModel):
    id: str
    name: str
    source_type: str
    source_url: str
    local_path: Optional[str] = None
    current_branch: Optional[str] = None
    languages: Optional[List[str]] = None
    status: str
    last_synced_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, project):
        """从 ORM 对象创建响应，处理 languages 字段"""
        import json
        data = {
            "id": project.id,
            "name": project.name,
            "source_type": project.source_type,
            "source_url": project.source_url,
            "local_path": project.local_path,
            "current_branch": project.current_branch,
            "status": project.status,
            "last_synced_at": project.last_synced_at,
            "created_at": project.created_at,
        }
        # 处理 languages 字段
        if project.languages:
            try:
                data["languages"] = json.loads(project.languages) if isinstance(project.languages, str) else project.languages
            except json.JSONDecodeError:
                data["languages"] = []
        else:
            data["languages"] = []
        return cls(**data)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    branch: Optional[str] = None
    config: Optional[dict] = None

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """创建新项目"""
    project_id = str(uuid.uuid4())

    local_path = None
    if project.source_type == "git":
        git_op = GitOperator(REPOS_PATH)
        try:
            # 验证仓库
            if not git_op.verify_repository(project.source_url):
                raise HTTPException(status_code=400, detail="无效的 Git 仓库 URL")

            # 克隆仓库
            local_path = git_op.clone(
                project.source_url,
                project_id,
                project.branch or "main"
            )
        except GitOperationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    db_project = Project(
        id=project_id,
        name=project.name,
        source_type=project.source_type,
        source_url=project.source_url,
        local_path=local_path,
        default_branch=project.branch,
        current_branch=project.branch,
        status="pending",
        config=str(project.config) if project.config else None
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return ProjectResponse.from_orm(db_project)

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取项目列表"""
    projects = db.query(Project).offset(skip).limit(limit).all()
    return [ProjectResponse.from_orm(p) for p in projects]

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取项目详情"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return ProjectResponse.from_orm(project)

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """更新项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    if update.name is not None:
        project.name = update.name
    if update.branch is not None:
        project.current_branch = update.branch
        # 切换分支
        if project.local_path and project.source_type == "git":
            git_op = GitOperator(REPOS_PATH)
            try:
                git_op.checkout(project.local_path, update.branch)
            except GitOperationError as e:
                raise HTTPException(status_code=400, detail=f"切换分支失败: {e}")
    if update.config is not None:
        project.config = str(update.config)

    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)

    return ProjectResponse.from_orm(project)

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """删除项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 删除本地文件
    if project.local_path:
        import shutil
        from pathlib import Path
        path = Path(project.local_path)
        if path.exists():
            shutil.rmtree(path)

    db.delete(project)
    db.commit()

    return {"message": "项目已删除"}

@router.post("/{project_id}/sync")
async def sync_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """同步项目（拉取最新代码）"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    if project.source_type != "git" or not project.local_path:
        raise HTTPException(status_code=400, detail="此项目类型不支持同步")

    git_op = GitOperator(REPOS_PATH)
    try:
        old_commit = git_op.get_current_commit(project.local_path)
        git_op.fetch(project.local_path)
        git_op.pull(project.local_path)
        new_commit = git_op.get_current_commit(project.local_path)

        # 更新状态
        project.last_commit_hash = new_commit
        project.last_synced_at = datetime.utcnow()
        project.status = "pending"  # 等待重新解析
        db.commit()

        return {
            "message": "同步成功",
            "old_commit": old_commit,
            "new_commit": new_commit,
            "has_changes": old_commit != new_commit
        }
    except GitOperationError as e:
        raise HTTPException(status_code=400, detail=f"同步失败: {e}")
