from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Microservice(Base):
    __tablename__ = "microservices"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)  # 服务名：user-service
    application_class = Column(String(255))
    port = Column(Integer)
    context_path = Column(String(255))
    config_file = Column(String(500))

    # 关系
    project = relationship("Project", back_populates="microservices")
    endpoints = relationship("RestEndpoint", back_populates="service", cascade="all, delete-orphan")
    feign_clients = relationship("FeignClient", back_populates="service", cascade="all, delete-orphan")
    domain_models = relationship("DomainModel", back_populates="service", cascade="all, delete-orphan")

class RestEndpoint(Base):
    __tablename__ = "rest_endpoints"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    service_id = Column(String(36), ForeignKey("microservices.id"), nullable=False)
    controller_class = Column(String(255), nullable=False)
    method_name = Column(String(255), nullable=False)
    http_method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    path = Column(String(255), nullable=False)
    full_path = Column(String(255), nullable=False)
    consumes = Column(Text)  # JSON array
    produces = Column(Text)  # JSON array
    parameters = Column(Text)  # JSON
    return_type = Column(String(255))
    file_path = Column(String(500))
    start_line = Column(Integer)

    service = relationship("Microservice", back_populates="endpoints")

class FeignClient(Base):
    __tablename__ = "feign_clients"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    service_id = Column(String(36), ForeignKey("microservices.id"), nullable=False)
    interface_name = Column(String(255), nullable=False)
    target_service = Column(String(255), nullable=False)
    path = Column(String(255))
    file_path = Column(String(500))
    start_line = Column(Integer)

    service = relationship("Microservice", back_populates="feign_clients")
    methods = relationship("FeignMethod", back_populates="client", cascade="all, delete-orphan")

class FeignMethod(Base):
    __tablename__ = "feign_methods"

    id = Column(String(36), primary_key=True)
    client_id = Column(String(36), ForeignKey("feign_clients.id"), nullable=False)
    name = Column(String(255), nullable=False)
    http_method = Column(String(10), nullable=False)
    path = Column(String(255))
    return_type = Column(String(255))
    parameters = Column(Text)  # JSON
    file_path = Column(String(500))
    start_line = Column(Integer)

    client = relationship("FeignClient", back_populates="methods")

class GatewayRoute(Base):
    __tablename__ = "gateway_routes"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    route_id = Column(String(255), nullable=False)
    source_path = Column(String(255), nullable=False)
    target_service = Column(String(255), nullable=False)
    predicates = Column(Text)  # JSON array
    filters = Column(Text)  # JSON array
    config_source = Column(String(20))  # JavaConfig, YAML
    file_path = Column(String(500))
    start_line = Column(Integer)

class ServiceCall(Base):
    __tablename__ = "service_calls"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    source_service = Column(String(255), nullable=False)
    target_service = Column(String(255), nullable=False)
    source_endpoint = Column(String(36), ForeignKey("rest_endpoints.id"))
    target_endpoint = Column(String(36), ForeignKey("rest_endpoints.id"))
    call_type = Column(String(20))  # feign, restTemplate, webClient
    is_async = Column(Boolean, default=False)
    circuit_breaker = Column(Boolean, default=False)

class DomainModel(Base):
    __tablename__ = "domain_models"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    service_id = Column(String(36), ForeignKey("microservices.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)  # aggregate, entity, value_object
    package = Column(String(255))
    annotations = Column(Text)  # JSON array
    file_path = Column(String(500))
    start_line = Column(Integer)

    service = relationship("Microservice", back_populates="domain_models")
    relationships = relationship("DomainRelationship", foreign_keys="DomainRelationship.source_id", back_populates="source")
    target_relationships = relationship("DomainRelationship", foreign_keys="DomainRelationship.target_id", back_populates="target")

class DomainRelationship(Base):
    __tablename__ = "domain_relationships"

    id = Column(String(36), primary_key=True)
    source_id = Column(String(36), ForeignKey("domain_models.id"), nullable=False)
    target_id = Column(String(36), ForeignKey("domain_models.id"), nullable=False)
    type = Column(String(20), nullable=False)  # one_to_one, one_to_many, many_to_one, many_to_many
    mapped_by = Column(String(255))
    join_column = Column(String(255))

    source = relationship("DomainModel", foreign_keys=[source_id], back_populates="relationships")
    target = relationship("DomainModel", foreign_keys=[target_id], back_populates="target_relationships")
