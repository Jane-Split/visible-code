from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json

from app.core.database import get_db
from app.core.config import REPOS_PATH
from app.models.project import Project
from app.models.entity import Entity
from app.models.graph import Dependency, FileIndex
from app.parser.scheduler import parse_scheduler

router = APIRouter(prefix="/api/projects/{project_id}/parser", tags=["parser"])

class ParseRequest(BaseModel):
    languages: Optional[List[str]] = None  # 指定要解析的语言
    force: bool = False  # 是否强制重新解析

class ParseProgress(BaseModel):
    project_id: str
    status: str  # pending, parsing, ready, error
    progress: float  # 0-100
    current_file: Optional[str] = None
    total_files: int = 0
    processed_files: int = 0

@router.post("/start")
async def start_parse(
    project_id: str,
    request: ParseRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """启动解析任务"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    if not project.local_path:
        raise HTTPException(status_code=400, detail="项目路径不存在")

    # 更新项目状态
    project.status = "parsing"
    db.commit()

    # 后台执行解析
    async def parse_task():
        try:
            # 执行解析
            result = await parse_scheduler.parse_project(
                project_id,
                project.local_path,
                request.languages
            )

            # 存储解析结果
            entities_data = result.get("entities", [])
            deps_data = result.get("dependencies", [])

            # 清除旧数据
            db.query(Entity).filter(Entity.project_id == project_id).delete()
            db.query(Dependency).filter(Dependency.project_id == project_id).delete()

            # 插入新实体
            entity_id_map = {}  # 旧ID -> 新ID
            for e_data in entities_data:
                entity = Entity(
                    id=e_data["id"],
                    project_id=project_id,
                    file_path=e_data.get("file_path", ""),
                    type=e_data.get("type", "unknown"),
                    name=e_data.get("name", ""),
                    qualified_name=e_data.get("qualified_name", ""),
                    start_line=e_data.get("start_line", 0),
                    end_line=e_data.get("end_line", 0),
                    modifiers=json.dumps(e_data.get("modifiers", [])),
                    annotations=json.dumps(e_data.get("annotations", [])),
                    signature=e_data.get("signature", ""),
                    docstring=e_data.get("docstring", "")
                )
                db.add(entity)
                entity_id_map[e_data["id"]] = e_data["id"]

            # 插入依赖关系（简化：直接使用名称映射）
            for d_data in deps_data:
                dep = Dependency(
                    id=d_data["id"],
                    project_id=project_id,
                    source_id=d_data.get("source_id", ""),
                    target_id=d_data.get("target_id", ""),
                    type=d_data.get("type", "reference"),
                    file_path=d_data.get("file_path", ""),
                    line=d_data.get("line", 0)
                )
                db.add(dep)

            db.commit()

            # 更新项目状态
            project.status = "ready"
            project.languages = json.dumps(request.languages or ["java", "typescript"])
            db.commit()

        except Exception as e:
            project.status = "error"
            db.commit()
            print(f"解析失败: {e}")

    # 启动后台任务
    asyncio.create_task(parse_task())

    return {"message": "解析任务已启动", "project_id": project_id}

@router.get("/status", response_model=ParseProgress)
async def get_parse_status(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取解析状态"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 统计已解析的实体数量
    total_entities = db.query(Entity).filter(Entity.project_id == project_id).count()

    return ParseProgress(
        project_id=project_id,
        status=project.status,
        progress=100 if project.status == "ready" else 50 if project.status == "parsing" else 0,
        total_files=0,
        processed_files=total_entities
    )

@router.get("/stats")
async def get_parse_stats(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取解析统计"""
    # 按类型统计实体
    type_stats = db.query(
        Entity.type,
        func.count(Entity.id).label("count")
    ).filter(Entity.project_id == project_id).group_by(Entity.type).all()

    # 统计依赖关系
    dep_stats = db.query(
        Dependency.type,
        func.count(Dependency.id).label("count")
    ).filter(Dependency.project_id == project_id).group_by(Dependency.type).all()

    return {
        "entities_by_type": {t: c for t, c in type_stats},
        "dependencies_by_type": {t: c for t, c in dep_stats},
        "total_entities": sum(c for _, c in type_stats),
        "total_dependencies": sum(c for _, c in dep_stats)
    }
