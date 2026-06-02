from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from app.core.database import get_db
from app.models.microservice import (
    Microservice, RestEndpoint, FeignClient, GatewayRoute,
    ServiceCall, DomainModel
)

router = APIRouter(prefix="/api/projects/{project_id}/microservices", tags=["microservices"])

# 响应模型
class MicroserviceResponse(BaseModel):
    id: str
    name: str
    application_class: Optional[str] = None
    port: Optional[int] = None

    class Config:
        from_attributes = True

class RestEndpointResponse(BaseModel):
    id: str
    service_id: str
    controller_class: str
    method_name: str
    http_method: str
    path: str
    full_path: str

class ServiceTopologyResponse(BaseModel):
    nodes: List[dict]
    edges: List[dict]

@router.get("/topology", response_model=ServiceTopologyResponse)
async def get_service_topology(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取服务拓扑图"""
    # 获取所有微服务
    services = db.query(Microservice).filter(Microservice.project_id == project_id).all()

    nodes = []
    for s in services:
        endpoints_count = db.query(RestEndpoint).filter(RestEndpoint.service_id == s.id).count()
        nodes.append({
            "id": s.id,
            "name": s.name,
            "type": "service",
            "instance_count": 1,  # 简化
            "endpoints": endpoints_count
        })

    # 获取服务间调用关系
    calls = db.query(ServiceCall).filter(ServiceCall.project_id == project_id).all()

    edges = []
    for c in calls:
        edges.append({
            "source": c.source_service,
            "target": c.target_service,
            "type": c.call_type or "feign",
            "async": c.is_async
        })

    return ServiceTopologyResponse(nodes=nodes, edges=edges)

@router.get("/", response_model=List[MicroserviceResponse])
async def list_services(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取微服务列表"""
    services = db.query(Microservice).filter(Microservice.project_id == project_id).all()
    return services

@router.get("/{service_id}")
async def get_service_detail(
    project_id: str,
    service_id: str,
    db: Session = Depends(get_db)
):
    """获取微服务详情"""
    service = db.query(Microservice).filter(
        Microservice.id == service_id,
        Microservice.project_id == project_id
    ).first()

    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")

    # 获取端点
    endpoints = db.query(RestEndpoint).filter(RestEndpoint.service_id == service_id).all()

    # 获取 FeignClient
    feign_clients = db.query(FeignClient).filter(FeignClient.service_id == service_id).all()

    return {
        "service": {
            "id": service.id,
            "name": service.name,
            "application_class": service.application_class,
            "port": service.port
        },
        "endpoints": [
            {
                "id": e.id,
                "controller_class": e.controller_class,
                "method_name": e.method_name,
                "http_method": e.http_method,
                "path": e.path
            }
            for e in endpoints
        ],
        "feign_clients": [
            {
                "id": f.id,
                "interface_name": f.interface_name,
                "target_service": f.target_service,
                "path": f.path
            }
            for f in feign_clients
        ]
    }

@router.get("/gateway-routes")
async def get_gateway_routes(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取网关路由配置"""
    routes = db.query(GatewayRoute).filter(GatewayRoute.project_id == project_id).all()

    result = []
    for r in routes:
        predicates = []
        filters = []
        try:
            if r.predicates:
                predicates = eval(r.predicates) if isinstance(r.predicates, str) else r.predicates
            if r.filters:
                filters = eval(r.filters) if isinstance(r.filters, str) else r.filters
        except:
            pass

        result.append({
            "id": r.id,
            "route_id": r.route_id,
            "source_path": r.source_path,
            "target_service": r.target_service,
            "predicates": predicates,
            "filters": filters
        })

    return result

@router.get("/domain-models")
async def get_domain_models(
    project_id: str,
    service_id: Optional[str] = Query(None, description="服务 ID"),
    db: Session = Depends(get_db)
):
    """获取领域模型"""
    query = db.query(DomainModel).filter(DomainModel.project_id == project_id)

    if service_id:
        query = query.filter(DomainModel.service_id == service_id)

    models = query.all()

    return [
        {
            "id": m.id,
            "name": m.name,
            "type": m.type,
            "service_id": m.service_id,
            "package": m.package,
        }
        for m in models
    ]

@router.post("/analyze")
async def analyze_microservices(
    project_id: str,
    db: Session = Depends(get_db)
):
    """分析微服务架构"""
    from app.models.project import Project
    from app.microservice.analyzer import SpringCloudAnalyzer

    # 获取项目
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    if not project.local_path:
        raise HTTPException(status_code=400, detail="项目路径不存在")

    # 执行分析
    analyzer = SpringCloudAnalyzer(project_id)
    analyzer.analyze_project(project.local_path)

    # 保存结果
    analyzer.save_to_database()

    result = analyzer.to_dict()

    return {
        "message": "微服务分析完成",
        "microservices_count": len(result['microservices']),
        "endpoints_count": len(result['endpoints']),
        "feign_clients_count": len(result['feign_clients']),
        "gateway_routes_count": len(result['gateway_routes']),
        "service_calls_count": len(result['service_calls']),
    }
