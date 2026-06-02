import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import Base, engine

@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_root():
    """测试根路径"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "CodeViz API" in response.json()["message"]

@pytest.mark.asyncio
async def test_create_project():
    """测试创建项目"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 测试本地项目创建
        response = await ac.post(
            "/api/projects/",
            json={
                "name": "Test Project",
                "source_type": "local",
                "source_url": "/tmp/test"
            }
        )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["source_type"] == "local"
    assert "id" in data

@pytest.mark.asyncio
async def test_list_projects():
    """测试获取项目列表"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/projects/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_project_not_found():
    """测试获取不存在的项目"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/projects/nonexistent-id")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_dependency_graph():
    """测试获取依赖图"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 先创建一个项目
        create_response = await ac.post(
            "/api/projects/",
            json={
                "name": "Graph Test Project",
                "source_type": "local",
                "source_url": "/tmp/test"
            }
        )
        project_id = create_response.json()["id"]

        # 获取依赖图
        response = await ac.get(f"/api/projects/{project_id}/graphs/dependency")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "total_nodes" in data
    assert "total_edges" in data

@pytest.mark.asyncio
async def test_get_parse_status():
    """测试获取解析状态"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 先创建一个项目
        create_response = await ac.post(
            "/api/projects/",
            json={
                "name": "Parse Test Project",
                "source_type": "local",
                "source_url": "/tmp/test"
            }
        )
        project_id = create_response.json()["id"]

        # 获取解析状态
        response = await ac.get(f"/api/projects/{project_id}/parser/status")
    assert response.status_code == 200
    data = response.json()
    assert "project_id" in data
    assert "status" in data
    assert "progress" in data

@pytest.mark.asyncio
async def test_get_parse_stats():
    """测试获取解析统计"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 先创建一个项目
        create_response = await ac.post(
            "/api/projects/",
            json={
                "name": "Stats Test Project",
                "source_type": "local",
                "source_url": "/tmp/test"
            }
        )
        project_id = create_response.json()["id"]

        # 获取解析统计
        response = await ac.get(f"/api/projects/{project_id}/parser/stats")
    assert response.status_code == 200
    data = response.json()
    assert "entities_by_type" in data
    assert "dependencies_by_type" in data
    assert "total_entities" in data
    assert "total_dependencies" in data

@pytest.mark.asyncio
async def test_list_microservices():
    """测试获取微服务列表"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 先创建一个项目
        create_response = await ac.post(
            "/api/projects/",
            json={
                "name": "Microservice Test Project",
                "source_type": "local",
                "source_url": "/tmp/test"
            }
        )
        project_id = create_response.json()["id"]

        # 获取微服务列表
        response = await ac.get(f"/api/projects/{project_id}/microservices/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_service_topology():
    """测试获取服务拓扑图"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 先创建一个项目
        create_response = await ac.post(
            "/api/projects/",
            json={
                "name": "Topology Test Project",
                "source_type": "local",
                "source_url": "/tmp/test"
            }
        )
        project_id = create_response.json()["id"]

        # 获取拓扑图
        response = await ac.get(f"/api/projects/{project_id}/microservices/topology")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data

@pytest.mark.asyncio
async def test_delete_project():
    """测试删除项目"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 先创建一个项目
        create_response = await ac.post(
            "/api/projects/",
            json={
                "name": "Delete Test Project",
                "source_type": "local",
                "source_url": "/tmp/test"
            }
        )
        project_id = create_response.json()["id"]

        # 删除项目
        delete_response = await ac.delete(f"/api/projects/{project_id}")
        assert delete_response.status_code == 200
        assert "message" in delete_response.json()

    # 使用新的客户端确认项目已被删除
    transport2 = ASGITransport(app=app)
    async with AsyncClient(transport=transport2, base_url="http://test") as ac2:
        get_response = await ac2.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 404
