import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import SessionLocal
from app.models.entity import Entity
from app.models.graph import FileIndex
from app.parser.scheduler import parse_scheduler
from app.watcher.git_poller import git_poller_manager
from app.watcher.file_watcher import file_watcher

logger = logging.getLogger(__name__)


class ChangeEventProcessor:
    """变更事件处理器"""

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._change_callbacks: List = []

    async def start(self) -> None:
        """启动处理器"""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._process_loop())
        logger.info("ChangeEventProcessor 已启动")

    async def stop(self) -> None:
        """停止处理器"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("ChangeEventProcessor 已停止")

    def add_callback(self, callback) -> None:
        """添加变更回调"""
        if callback not in self._change_callbacks:
            self._change_callbacks.append(callback)

    def remove_callback(self, callback) -> None:
        """移除变更回调"""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

    async def push_event(self, event: Dict[str, Any]) -> None:
        """推送事件到队列"""
        await self._queue.put(event)

    async def _process_loop(self) -> None:
        """事件处理循环"""
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"处理事件失败: {e}")

    async def _process_event(self, event: Dict[str, Any]) -> None:
        """处理单个事件"""
        project_id = event.get('project_id')
        event_type = event.get('event_type')
        file_path = event.get('file_path')

        logger.info(f"处理变更事件: {project_id} - {event_type} - {file_path}")

        try:
            if event_type == 'deleted':
                await self._handle_file_deleted(project_id, file_path)
            else:
                await self._handle_file_changed(project_id, file_path)

            # 触发回调
            await self._notify_callbacks(event)

        except Exception as e:
            logger.error(f"处理文件变更失败: {e}")

    async def _handle_file_deleted(self, project_id: str, file_path: str) -> None:
        """处理文件删除"""
        db = SessionLocal()
        try:
            # 从数据库删除相关实体
            db.query(Entity).filter(
                Entity.project_id == project_id,
                Entity.file_path == file_path
            ).delete()

            # 删除文件索引
            db.query(FileIndex).filter(
                FileIndex.project_id == project_id,
                FileIndex.file_path == file_path
            ).delete()

            db.commit()
            logger.info(f"已删除文件相关数据: {file_path}")
        finally:
            db.close()

    async def _handle_file_changed(self, project_id: str, file_path: str) -> None:
        """处理文件变更"""
        # 使用解析器重新解析文件
        result = await parse_scheduler.parse_file(project_id, file_path)

        if 'error' in result:
            logger.warning(f"解析失败: {file_path} - {result['error']}")
            return

        db = SessionLocal()
        try:
            # 删除旧数据
            db.query(Entity).filter(
                Entity.project_id == project_id,
                Entity.file_path == file_path
            ).delete()

            # 插入新数据
            for entity_data in result.get('entities', []):
                entity = Entity(
                    id=entity_data['id'],
                    project_id=project_id,
                    file_path=file_path,
                    type=entity_data.get('type', 'unknown'),
                    name=entity_data.get('name', ''),
                    qualified_name=entity_data.get('qualified_name', ''),
                    start_line=entity_data.get('start_line', 0),
                    end_line=entity_data.get('end_line', 0),
                )
                db.add(entity)

            db.commit()
            logger.info(f"已更新文件数据: {file_path}, 实体数: {len(result.get('entities', []))}")
        finally:
            db.close()

    async def _notify_callbacks(self, event: Dict[str, Any]) -> None:
        """通知所有回调"""
        for callback in self._change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"回调执行失败: {e}")


class ProjectWatcherManager:
    """项目监听管理器"""

    def __init__(self):
        self._processor = ChangeEventProcessor()
        self._running = False

    async def start(self) -> None:
        """启动管理器"""
        if self._running:
            return
        self._running = True
        await self._processor.start()
        logger.info("ProjectWatcherManager 已启动")

    async def stop(self) -> None:
        """停止管理器"""
        self._running = False
        await self._processor.stop()
        logger.info("ProjectWatcherManager 已停止")

    async def watch_project(self, project_id: str, repo_path: str, source_type: str) -> None:
        """监听项目"""
        # 启动处理器
        if not self._running:
            await self.start()

        # 添加变更回调
        self._processor.add_callback(self._on_project_change)

        if source_type == 'local':
            # 本地项目：启动文件监听
            await file_watcher.start_watching(
                project_id,
                repo_path,
                self._processor.push_event
            )
        else:
            # Git 项目：启动文件监听 + Git 轮询
            await file_watcher.start_watching(
                project_id,
                repo_path,
                self._processor.push_event
            )

            await git_poller_manager.create_poller(
                project_id,
                repo_path,
                interval=30,
                on_change_callback=self._processor.push_event
            )

    async def unwatch_project(self, project_id: str) -> None:
        """取消监听项目"""
        await file_watcher.stop_watching(project_id)
        await git_poller_manager.stop_poller(project_id)

    async def _on_project_change(self, event: Dict[str, Any]) -> None:
        """项目变更回调"""
        logger.info(f"项目变更: {event}")
        # 可以在此触发 WebSocket 推送等


# 全局实例
project_watcher_manager = ProjectWatcherManager()
