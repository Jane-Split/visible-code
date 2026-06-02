from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from pydantic import BaseModel

from app.core.database import get_db
from app.models.entity import Entity
from app.models.graph import Dependency, CallChain

router = APIRouter(prefix="/api/projects/{project_id}/graphs", tags=["graphs"])

class GraphNode(BaseModel):
    id: str
    name: str
    type: str
    qualified_name: Optional[str] = None
    file_path: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    modifiers: Optional[List[str]] = []
    annotations: Optional[List[str]] = []

class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    file_path: Optional[str] = None
    line: Optional[int] = None

class DependencyGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_nodes: int
    total_edges: int

@router.get("/dependency", response_model=DependencyGraph)
async def get_dependency_graph(
    project_id: str,
    root_id: Optional[str] = Query(None, description="根节点 ID"),
    depth: int = Query(2, ge=1, le=10, description="展开深度"),
    entity_type: Optional[str] = Query(None, description="实体类型过滤"),
    db: Session = Depends(get_db)
):
    """获取依赖图"""
    # 查询实体
    query = db.query(Entity).filter(Entity.project_id == project_id)
    if entity_type:
        query = query.filter(Entity.type == entity_type)

    entities = query.all()

    # 构建节点
    nodes = []
    for e in entities:
        modifiers = []
        annotations = []
        try:
            if e.modifiers:
                modifiers = eval(e.modifiers) if isinstance(e.modifiers, str) else e.modifiers
            if e.annotations:
                annotations = eval(e.annotations) if isinstance(e.annotations, str) else e.annotations
        except:
            pass

        nodes.append(GraphNode(
            id=e.id,
            name=e.name,
            type=e.type,
            qualified_name=e.qualified_name,
            file_path=e.file_path,
            start_line=e.start_line,
            end_line=e.end_line,
            modifiers=modifiers,
            annotations=annotations
        ))

    # 查询依赖关系
    deps = db.query(Dependency).filter(Dependency.project_id == project_id).all()

    edges = []
    for d in deps:
        edges.append(GraphEdge(
            source=d.source_id,
            target=d.target_id,
            type=d.type,
            file_path=d.file_path,
            line=d.line
        ))

    return DependencyGraph(
        nodes=nodes,
        edges=edges,
        total_nodes=len(nodes),
        total_edges=len(edges)
    )

@router.get("/call-chain")
async def get_call_chain(
    project_id: str,
    method_id: Optional[str] = Query(None, description="起始方法 ID"),
    direction: str = Query("down", description="up/down/both"),
    max_depth: int = Query(5, ge=1, le=20, description="最大深度"),
    db: Session = Depends(get_db)
):
    """获取调用链"""
    # 获取所有调用关系
    calls = db.query(CallChain).filter(CallChain.project_id == project_id).all()

    # 构建调用图
    call_graph = {}
    for call in calls:
        if call.caller_id not in call_graph:
            call_graph[call.caller_id] = []
        call_graph[call.caller_id].append({
            "callee_id": call.callee_id,
            "file_path": call.file_path,
            "line": call.line
        })

    # BFS 遍历调用链
    def traverse(start_id, direction, max_depth):
        result = []
        visited = set()
        queue = [(start_id, 0, direction)]

        while queue:
            node_id, depth, dir_ = queue.pop(0)
            if depth >= max_depth or node_id in visited:
                continue
            visited.add(node_id)

            if dir_ in ["down", "both"]:
                for callee in call_graph.get(node_id, []):
                    result.append({
                        "from": node_id,
                        "to": callee["callee_id"],
                        "file_path": callee["file_path"],
                        "line": callee["line"],
                        "depth": depth + 1
                    })
                    queue.append((callee["callee_id"], depth + 1, "down"))

            if dir_ in ["up", "both"]:
                # 反向查找
                for caller_id, callees in call_graph.items():
                    if any(c["callee_id"] == node_id for c in callees):
                        result.append({
                            "from": caller_id,
                            "to": node_id,
                            "depth": depth + 1
                        })
                        queue.append((caller_id, depth + 1, "up"))

        return result

    if method_id:
        chain = traverse(method_id, direction, max_depth)
    else:
        chain = []
        for start_id in call_graph.keys():
            chain.extend(traverse(start_id, direction, max_depth))

    return {"calls": chain, "total": len(chain)}

@router.get("/entity/{entity_id}")
async def get_entity(
    project_id: str,
    entity_id: str,
    db: Session = Depends(get_db)
):
    """获取实体详情"""
    entity = db.query(Entity).filter(
        Entity.id == entity_id,
        Entity.project_id == project_id
    ).first()

    if not entity:
        raise HTTPException(status_code=404, detail="实体不存在")

    # 获取子实体
    children = db.query(Entity).filter(
        Entity.parent_id == entity_id,
        Entity.project_id == project_id
    ).all()

    # 获取依赖关系
    deps_from = db.query(Dependency).filter(
        Dependency.source_id == entity_id,
        Dependency.project_id == project_id
    ).all()

    deps_to = db.query(Dependency).filter(
        Dependency.target_id == entity_id,
        Dependency.project_id == project_id
    ).all()

    modifiers = []
    annotations = []
    try:
        if entity.modifiers:
            modifiers = eval(entity.modifiers) if isinstance(entity.modifiers, str) else entity.modifiers
        if entity.annotations:
            annotations = eval(entity.annotations) if isinstance(entity.annotations, str) else entity.annotations
    except:
        pass

    return {
        "entity": {
            "id": entity.id,
            "name": entity.name,
            "qualified_name": entity.qualified_name,
            "type": entity.type,
            "file_path": entity.file_path,
            "start_line": entity.start_line,
            "end_line": entity.end_line,
            "modifiers": modifiers,
            "annotations": annotations,
            "signature": entity.signature,
            "docstring": entity.docstring
        },
        "children": [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "signature": c.signature
            }
            for c in children
        ],
        "dependencies_from": [
            {"target_id": d.target_id, "type": d.type, "line": d.line}
            for d in deps_from
        ],
        "dependencies_to": [
            {"source_id": d.source_id, "type": d.type, "line": d.line}
            for d in deps_to
        ]
    }
