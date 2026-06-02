from app.api.projects import router as projects_router
from app.api.graphs import router as graphs_router
from app.api.parser import router as parser_router
from app.api.microservices import router as microservices_router

__all__ = [
    "projects_router",
    "graphs_router",
    "parser_router",
    "microservices_router",
]
