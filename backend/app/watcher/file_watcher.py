import asyncio
import logging
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

logger = logging.getLogger(__name__)


class CodeFileEventHandler(FileSystemEventHandler):
    """代码文件事件处理器"""

    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = {
        '.java', '.ts', '.tsx', '.js', '.jsx', '.py', '.go',
        '.yaml', '.yml', '.xml', '.properties'
    }

    # 忽略的目录
    IGNORED_DIRS = {
        'node_modules', '.git', 'target', 'dist', 'build',
        '__pycache__', '.idea', '.vscode', 'bin', 'obj'
    }

    def __init__(self, project_id: str, event_callback: Callable):
        self.project_id = project_id
        self.event_callback = event_callback
        self._debounce_timers: Dict[str, asyncio.Task] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _should_process(self, path: str) -> bool:
        """判断是否应该处理此文件"""
        path_obj = Path(path)

        # 忽略目录
        for part in path_obj.parts:
            if part in self.IGNORED_DIRS:
                return False

        # 只处理支持的扩展名
        if path_obj.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False

        return True

    def _debounce(self, file_path: str, event_type: str) -> None:
        """防抖处理"""
        # 取消已有的定时器
        if file_path in self._debounce_timers:
            self._debounce_timers[file_path].cancel()

        # 创建新的定时器
        if self._loop and self._loop.is_running():
            task = self._loop.create_task(
                self._emit_event(file_path, event_type)
            )
            self._debounce_timers[file_path] = task

    async def _emit_event(self, file_path: str, event_type: str) -> None:
        """延迟发送事件"""
        await asyncio.sleep(0.5)  # 500ms 防抖

        event = {
            'project_id': self.project_id,
            'file_path': file_path,
            'event_type': event_type,  # created, modified, deleted
            'timestamp': None
        }

        await self.event_callback(event)

        # 清理定时器
        if file_path in self._debounce_timers:
            del self._debounce_timers[file_path]

    def _schedule_event(self, file_path: str, event_type: str) -> None:
        """调度事件"""
        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)

        # 在主线程创建任务
        if self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._emit_event(file_path, event_type),
                self._loop
            )
        else:
            self._loop.run_until_complete(self._emit_event(file_path, event_type))

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self._should_process(event.src_path):
            logger.info(f"文件创建: {event.src_path}")
            self._schedule_event(event.src_path, 'created')

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self._should_process(event.src_path):
            logger.info(f"文件修改: {event.src_path}")
            self._schedule_event(event.src_path, 'modified')

    def on_deleted(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self._should_process(event.src_path):
            logger.info(f"文件删除: {event.src_path}")
            self._schedule_event(event.src_path, 'deleted')


class FileWatcher:
    """文件监听器管理器"""

    _instance = None
    _watchers: Dict[str, Observer] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def start_watching(
        self,
        project_id: str,
        watch_path: str,
        event_callback: Callable
    ) -> None:
        """启动文件监听"""
        if project_id in self._watchers:
            logger.warning(f"项目 {project_id} 已在监听中")
            return

        loop = asyncio.get_event_loop()

        # 创建事件处理器
        handler = CodeFileEventHandler(project_id, event_callback)
        handler._loop = loop

        # 创建观察者
        observer = Observer()
        observer.schedule(handler, watch_path, recursive=True)
        observer.start()

        self._watchers[project_id] = observer
        logger.info(f"开始监听项目 {project_id}: {watch_path}")

    async def stop_watching(self, project_id: str) -> None:
        """停止文件监听"""
        if project_id in self._watchers:
            observer = self._watchers[project_id]
            observer.stop()
            observer.join(timeout=5)
            del self._watchers[project_id]
            logger.info(f"停止监听项目 {project_id}")

    def is_watching(self, project_id: str) -> bool:
        """检查是否正在监听"""
        return project_id in self._watchers


# 全局实例
file_watcher = FileWatcher()
