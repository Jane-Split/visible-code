"""SpringCloud 微服务分析器"""
from typing import List, Dict, Optional
from pathlib import Path
import re
import uuid
from dataclasses import dataclass, field

from app.core.database import SessionLocal
from app.models.microservice import (
    Microservice, RestEndpoint, FeignClient, FeignMethod,
    GatewayRoute, ServiceCall, DomainModel, DomainRelationship
)


@dataclass
class MicroserviceInfo:
    """微服务信息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    application_class: str = ""
    port: int = 0
    context_path: str = ""
    config_file: str = ""
    file_path: str = ""


@dataclass
class RestEndpointInfo:
    """REST端点信息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str = ""
    controller_class: str = ""
    method_name: str = ""
    http_method: str = ""
    path: str = ""
    full_path: str = ""
    return_type: str = ""
    file_path: str = ""
    start_line: int = 0


@dataclass
class FeignClientInfo:
    """FeignClient信息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str = ""
    interface_name: str = ""
    target_service: str = ""
    path: str = ""
    file_path: str = ""
    methods: List = field(default_factory=list)


@dataclass
class GatewayRouteInfo:
    """网关路由信息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    route_id: str = ""
    source_path: str = ""
    target_service: str = ""
    predicates: List = field(default_factory=list)
    filters: List = field(default_factory=list)
    config_source: str = ""


class SpringCloudAnalyzer:
    """SpringCloud微服务分析器"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.microservices: Dict[str, MicroserviceInfo] = {}
        self.endpoints: List[RestEndpointInfo] = []
        self.feign_clients: List[FeignClientInfo] = []
        self.gateway_routes: List[GatewayRouteInfo] = []
        self.service_calls: List[Dict] = []
    
    def analyze_project(self, project_path: str) -> None:
        """分析整个项目"""
        project = Path(project_path)
        
        for java_file in project.rglob("*.java"):
            if self._should_skip(java_file):
                continue
            
            try:
                with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if self._is_application_class(content):
                    service = self._parse_application_class(java_file, content)
                    if service:
                        self.microservices[service.name] = service
                
                if '@RestController' in content or '@RequestMapping' in content:
                    endpoints = self._parse_controller(java_file, content)
                    self.endpoints.extend(endpoints)
                
                if '@FeignClient' in content:
                    feign = self._parse_feign_client(java_file, content)
                    if feign:
                        self.feign_clients.append(feign)
                
                if 'RouteLocator' in content:
                    routes = self._parse_gateway(java_file, content)
                    self.gateway_routes.extend(routes)
            except Exception as e:
                print(f"分析文件失败 {java_file}: {e}")
    
    def _should_skip(self, file_path: Path) -> bool:
        skip_dirs = {'node_modules', 'target', '.git', 'test'}
        for part in file_path.parts:
            if part in skip_dirs:
                return True
        return file_path.match("*Test.java")
    
    def _is_application_class(self, content: str) -> bool:
        return '@SpringBootApplication' in content or '@EnableEurekaClient' in content
    
    def _parse_application_class(self, file_path: str, content: str) -> Optional[MicroserviceInfo]:
        class_match = re.search(r'class\s+(\w+)', content)
        if not class_match:
            return None
        
        class_name = class_match.group(1)
        service_name = self._extract_service_name(file_path, class_name)
        port = self._extract_port(content)
        
        return MicroserviceInfo(
            name=service_name,
            application_class=class_name,
            port=port,
            file_path=file_path
        )
    
    def _extract_service_name(self, file_path: str, class_name: str) -> str:
        path_parts = Path(file_path).parts
        for i, part in enumerate(path_parts):
            if part == 'src' and i + 2 < len(path_parts):
                potential = path_parts[i + 1]
                if potential not in {'main', 'test', 'java'}:
                    return potential
        
        if class_name.endswith('Application'):
            return class_name[:-11].lower() + "-service"
        return class_name.lower() + "-service"
    
    def _extract_port(self, content: str) -> int:
        match = re.search(r'server\.port\s*=\s*(\d+)', content)
        return int(match.group(1)) if match else 8080
    
    def _parse_controller(self, file_path: str, content: str) -> List[RestEndpointInfo]:
        endpoints = []
        
        # 类级别路径
        class_path = ""
        class_match = re.search(r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']', content)
        if class_match:
            class_path = class_match.group(1)
        
        service_id = self._find_service_for_file(file_path)
        
        # HTTP方法模式
        for match in re.finditer(r'@(Get|Post|Put|Delete|Patch|RequestMapping)\s*\([^)]*\)', content):
            http_method = match.group(1).upper()
            if http_method == 'REQUESTMAPPING':
                rm_match = re.search(r'method\s*=\s*RequestMethod\.(\w+)', match.group(0))
                http_method = rm_match.group(1).upper() if rm_match else 'GET'
            
            # 查找方法名
            start = match.end()
            method_match = re.search(r'(?:public|private)\s+\w+(?:<[^>]+>)?\s+(\w+)\s*\(', content[start:start+200])
            if method_match:
                method_name = method_match.group(1)
                method_path = re.search(r'value\s*=\s*["\']([^"\']+)["\']', match.group(0)) or \
                              re.search(r'path\s*=\s*["\']([^"\']+)["\']', match.group(0))
                
                path = method_path.group(1) if method_path else ""
                
                endpoint = RestEndpointInfo(
                    service_id=service_id,
                    controller_class=Path(file_path).stem,
                    method_name=method_name,
                    http_method=http_method,
                    path=path,
                    full_path=class_path + path,
                    file_path=file_path
                )
                endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_feign_client(self, file_path: str, content: str) -> Optional[FeignClientInfo]:
        client_match = re.search(r"@FeignClient\s*\(\s*(?:name\s*=\s*)?[\"']?([^\"'()]+)", content)
        if not client_match:
            return None
        
        target_service = client_match.group(1).strip()
        
        class_match = re.search(r'interface\s+(\w+)', content)
        interface_name = class_match.group(1) if class_match else ""
        
        path_match = re.search(r'path\s*=\s*["\']([^"\']+)["\']', content)
        path = path_match.group(1) if path_match else ""
        
        service_id = self._find_service_for_file(file_path)
        
        # 解析方法
        methods = []
        for m in re.finditer(r'@(Get|Post|Put|Delete|Patch)\s*\([^)]*\)\s*(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\(', content):
            methods.append({
                'name': m.group(2),
                'http_method': m.group(1).upper()
            })
        
        return FeignClientInfo(
            service_id=service_id,
            interface_name=interface_name,
            target_service=target_service,
            path=path,
            file_path=file_path,
            methods=methods
        )
    
    def _parse_gateway(self, file_path: str, content: str) -> List[GatewayRouteInfo]:
        routes = []
        
        for match in re.finditer(r'\.(?:route|path)\s*\(\s*"([^"]+)"\s*,\s*r\s*->', content):
            route_id = match.group(1)
            
            # 查找uri
            start = match.end()
            uri_match = re.search(r'\.uri\s*\(\s*["\']*lb://([^)"]+)', content[start:start+300])
            target_service = uri_match.group(1) if uri_match else ""
            
            # 查找predicates
            predicates = []
            pred_match = re.search(r'Path\s*\(\s*["\']([^"\']+)["\']', content[start:start+300])
            if pred_match:
                predicates.append(pred_match.group(1))
            
            routes.append(GatewayRouteInfo(
                route_id=route_id,
                source_path=predicates[0] if predicates else "",
                target_service=target_service,
                predicates=predicates,
                config_source="JavaConfig"
            ))
        
        return routes
    
    def _find_service_for_file(self, file_path: str) -> str:
        for service in self.microservices.values():
            if service.file_path:
                service_dir = str(Path(service.file_path).parent)
                if service_dir in str(file_path):
                    return service.id
        return list(self.microservices.values())[0].id if self.microservices else ""
    
    def build_service_calls(self) -> None:
        """构建服务间调用关系"""
        for feign in self.feign_clients:
            if feign.service_id and feign.target_service:
                self.service_calls.append({
                    'source_service': feign.service_id,
                    'target_service': feign.target_service,
                    'call_type': 'feign'
                })
    
    def save_to_database(self) -> None:
        """保存到数据库"""
        db = SessionLocal()
        try:
            for service in self.microservices.values():
                db.add(Microservice(
                    id=service.id,
                    project_id=self.project_id,
                    name=service.name,
                    application_class=service.application_class,
                    port=service.port,
                    context_path=service.context_path
                ))
            
            for endpoint in self.endpoints:
                db.add(RestEndpoint(
                    id=endpoint.id,
                    project_id=self.project_id,
                    service_id=endpoint.service_id,
                    controller_class=endpoint.controller_class,
                    method_name=endpoint.method_name,
                    http_method=endpoint.http_method,
                    path=endpoint.path,
                    full_path=endpoint.full_path,
                    return_type=endpoint.return_type,
                    file_path=endpoint.file_path,
                    start_line=endpoint.start_line
                ))
            
            for feign in self.feign_clients:
                db.add(FeignClient(
                    id=feign.id,
                    project_id=self.project_id,
                    service_id=feign.service_id,
                    interface_name=feign.interface_name,
                    target_service=feign.target_service,
                    path=feign.path,
                    file_path=feign.file_path
                ))
            
            for route in self.gateway_routes:
                db.add(GatewayRoute(
                    id=route.id,
                    project_id=self.project_id,
                    route_id=route.route_id,
                    source_path=route.source_path,
                    target_service=route.target_service,
                    predicates=str(route.predicates),
                    filters=str(route.filters),
                    config_source=route.config_source
                ))
            
            self.build_service_calls()
            for call in self.service_calls:
                db.add(ServiceCall(
                    id=str(uuid.uuid4()),
                    project_id=self.project_id,
                    source_service=call['source_service'],
                    target_service=call['target_service'],
                    call_type=call.get('call_type', 'feign')
                ))
            
            db.commit()
        finally:
            db.close()
    
    def to_dict(self) -> Dict:
        self.build_service_calls()
        return {
            'microservices': [{'id': s.id, 'name': s.name, 'port': s.port} for s in self.microservices.values()],
            'endpoints': [{'id': e.id, 'service_id': e.service_id, 'http_method': e.http_method, 'path': e.path} for e in self.endpoints],
            'feign_clients': [{'id': f.id, 'target_service': f.target_service, 'methods': f.methods} for f in self.feign_clients],
            'gateway_routes': [{'id': r.id, 'route_id': r.route_id, 'source_path': r.source_path, 'target_service': r.target_service} for r in self.gateway_routes],
            'service_calls': self.service_calls
        }
