from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.core.websocket import ws_handler
from app.api import projects_router, graphs_router, parser_router, microservices_router

app = FastAPI(
    title="CodeViz API",
    description="企业级代码可视化平台 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(projects_router)
app.include_router(graphs_router)
app.include_router(parser_router)
app.include_router(microservices_router)


@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库"""
    init_db()


@app.websocket("/ws/projects/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket 端点"""
    await ws_handler.handle_connection(websocket, project_id)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
async def root():
    return {
        "message": "CodeViz API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
