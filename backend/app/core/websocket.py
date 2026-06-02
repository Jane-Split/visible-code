import asyncio
import json
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # {project_id: {websocket: connection}}
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, project_id: str, websocket: WebSocket) -> None:
        """建立连接"""
        await websocket.accept()

        async with self._lock:
            if project_id not in self._connections:
                self._connections[project_id] = set()
            self._connections[project_id].add(websocket)

        logger.info(f"WebSocket 连接已建立: {project_id}, 当前连接数: {len(self._connections.get(project_id, []))}")

        # 发送连接成功消息
        await self.send_personal_message({
            'type': 'connected',
            'payload': {
                'project_id': project_id,
                'message': '连接成功'
            }
        }, websocket)

    async def disconnect(self, project_id: str, websocket: WebSocket) -> None:
        """断开连接"""
        async with self._lock:
            if project_id in self._connections:
                self._connections[project_id].discard(websocket)
                if not self._connections[project_id]:
                    del self._connections[project_id]

        logger.info(f"WebSocket 连接已断开: {project_id}")

    async def send_personal_message(self, message: Dict, websocket: WebSocket) -> None:
        """发送个人消息"""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")

    async def broadcast(self, project_id: str, message: Dict) -> None:
        """广播消息到项目所有连接"""
        async with self._lock:
            connections = self._connections.get(project_id, set()).copy()

        disconnected = []

        for websocket in connections:
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json(message)
                else:
                    disconnected.append(websocket)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected.append(websocket)

        # 清理断开的连接
        if disconnected:
            async with self._lock:
                for ws in disconnected:
                    self._connections.get(project_id, set()).discard(ws)

    async def send_parsing_progress(
        self,
        project_id: str,
        progress: float,
        current_file: str,
        total_files: int,
        processed_files: int
    ) -> None:
        """发送解析进度"""
        await self.broadcast(project_id, {
            'type': 'parsing_progress',
            'payload': {
                'progress': progress,
                'current_file': current_file,
                'total_files': total_files,
                'processed_files': processed_files
            }
        })

    async def send_change_event(self, project_id: str, events: list) -> None:
        """发送代码变更事件"""
        await self.broadcast(project_id, {
            'type': 'change_event',
            'payload': events
        })

    def get_connection_count(self, project_id: str) -> int:
        """获取项目连接数"""
        return len(self._connections.get(project_id, set()))

    def get_all_projects(self) -> Set[str]:
        """获取所有正在监听的项目"""
        return set(self._connections.keys())


# 全局实例
ws_manager = ConnectionManager()


class WebSocketHandler:
    """WebSocket 处理器"""

    def __init__(self):
        self.ws_manager = ws_manager

    async def handle_connection(self, websocket: WebSocket, project_id: str) -> None:
        """处理 WebSocket 连接"""
        await self.ws_manager.connect(project_id, websocket)

        try:
            while True:
                # 接收客户端消息
                data = await websocket.receive_text()
                message = json.loads(data)

                # 处理客户端消息
                await self._handle_message(project_id, websocket, message)

        except Exception as e:
            logger.error(f"WebSocket 处理异常: {e}")
        finally:
            await self.ws_manager.disconnect(project_id, websocket)

    async def _handle_message(self, project_id: str, websocket: WebSocket, message: Dict) -> None:
        """处理客户端消息"""
        msg_type = message.get('type')

        if msg_type == 'ping':
            await self.ws_manager.send_personal_message({
                'type': 'pong',
                'payload': {'timestamp': message.get('timestamp')}
            }, websocket)

        elif msg_type == 'subscribe':
            # 客户端订阅项目
            logger.info(f"客户端订阅项目: {project_id}")

        elif msg_type == 'unsubscribe':
            # 客户端取消订阅
            logger.info(f"客户端取消订阅项目: {project_id}")
            await self.ws_manager.disconnect(project_id, websocket)


# 全局实例
ws_handler = WebSocketHandler()
