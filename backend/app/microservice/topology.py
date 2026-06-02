"""服务拓扑构建器"""
from typing import List, Dict
from dataclasses import dataclass

from app.core.database import SessionLocal
from app.models.microservice import Microservice, ServiceCall, RestEndpoint


@dataclass
class ServiceNode:
    """服务节点"""
    id: str
    name: str
    type: str = "service"
    status: str = "healthy"
    instance_count: int = 1
    endpoint_count: int = 0


@dataclass
class ServiceEdge:
    """服务调用边"""
    source: str
    target: str
    type: str = "sync"
    call_count: int = 0


class TopologyBuilder:
    """服务拓扑构建器"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.nodes: List[ServiceNode] = []
        self.edges: List[ServiceEdge] = []
    
    def build(self) -> Dict:
        """构建拓扑"""
        db = SessionLocal()
        try:
            # 获取所有微服务
            services = db.query(Microservice).filter(
                Microservice.project_id == self.project_id
            ).all()
            
            for service in services:
                endpoint_count = db.query(RestEndpoint).filter(
                    RestEndpoint.service_id == service.id
                ).count()
                
                self.nodes.append(ServiceNode(
                    id=service.id,
                    name=service.name,
                    type="service",
                    endpoint_count=endpoint_count
                ))
            
            # 获取调用关系
            calls = db.query(ServiceCall).filter(
                ServiceCall.project_id == self.project_id
            ).all()
            
            seen = set()
            for call in calls:
                edge_key = (call.source_service, call.target_service)
                if edge_key not in seen:
                    seen.add(edge_key)
                    self.edges.append(ServiceEdge(
                        source=call.source_service,
                        target=call.target_service,
                        type="sync" if call.call_type == "feign" else "async"
                    ))
            
            return self.to_dict()
        finally:
            db.close()
    
    def to_dict(self) -> Dict:
        return {
            'nodes': [
                {'id': n.id, 'name': n.name, 'type': n.type, 'status': n.status, 'endpoint_count': n.endpoint_count}
                for n in self.nodes
            ],
            'edges': [
                {'source': e.source, 'target': e.target, 'type': e.type}
                for e in self.edges
            ]
        }
