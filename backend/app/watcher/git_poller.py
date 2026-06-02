import asyncio
import logging
from typing import Optional, Callable
from datetime import datetime

from app.core.git import GitOperator, GitOperationError
from app.core.config import REPOS_PATH

logger = logging.getLogger(__name__)


class GitPoller:
    """Git 轮询器"""

    def __init__(
        self,
        project_id: str,
        repo_path: str,
        interval: int = 30,
        on_change_callback: Optional[Callable] = None
    ):
        self.project_id = project_id
        self.repo_path = repo_path
        self.interval = interval  # 轮询间隔（秒）
        self.on_change_callback = on_change_callback
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._git_op = GitOperator(REPOS_PATH)
        self._last_commit: Optional[str] = None

    async def start(self) -> None:
        """启动轮询"""
        if self._running:
            logger.warning(f"GitPoller {self.project_id} 已在运行")
            return

        self._running = True

        # 获取初始 commit
        try:
            self._last_commit = self._git_op.get_current_commit(self.repo_path)
            logger.info(f"GitPoller {self.project_id} 启动，当前 commit: {self._last_commit}")
        except GitOperationError as e:
            logger.error(f"获取初始 commit 失败: {e}")

        # 启动轮询循环
        self._task = asyncio.create_task(self._poll_loop())

    async def stop(self) -> None:
        """停止轮询"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info(f"GitPoller {self.project_id} 已停止")

    async def _poll_loop(self) -> None:
        """轮询循环"""
        while self._running:
            try:
                await self._check_changes()
            except Exception as e:
                logger.error(f"轮询检查失败: {e}")

            await asyncio.sleep(self.interval)

    async def _check_changes(self) -> None:
        """检查远程变更"""
        try:
            # Fetch 最新
            self._git_op.fetch(self.repo_path)

            # 获取远程最新 commit
            remote_commit = self._git_op.get_remote_commit(self.repo_path)

            if remote_commit != self._last_commit:
                logger.info(f"检测到远程变更: {self._last_commit} -> {remote_commit}")

                # 获取变更文件列表
                changes = self._git_op.get_changed_files(
                    self.repo_path,
                    self._last_commit,
                    remote_commit
                )

                # 触发回调
                if self.on_change_callback:
                    await self.on_change_callback({
                        'project_id': self.project_id,
                        'old_commit': self._last_commit,
                        'new_commit': remote_commit,
                        'changes': changes,
                        'timestamp': datetime.utcnow().isoformat()
                    })

                # 更新 commit
                self._last_commit = remote_commit

                # Pull 最新代码
                self._git_op.pull(self.repo_path)

        except GitOperationError as e:
            logger.error(f"检查变更失败: {e}")

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running


class GitPollerManager:
    """Git 轮询器管理器"""

    _instance = None
    _pollers: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def create_poller(
        self,
        project_id: str,
        repo_path: str,
        interval: int = 30,
        on_change_callback: Optional[Callable] = None
    ) -> GitPoller:
        """创建轮询器"""
        if project_id in self._pollers:
            await self.stop_poller(project_id)

        poller = GitPoller(
            project_id=project_id,
            repo_path=repo_path,
            interval=interval,
            on_change_callback=on_change_callback
        )
        self._pollers[project_id] = poller
        await poller.start()

        return poller

    async def stop_poller(self, project_id: str) -> None:
        """停止轮询器"""
        if project_id in self._pollers:
            await self._pollers[project_id].stop()
            del self._pollers[project_id]

    def get_poller(self, project_id: str) -> Optional[GitPoller]:
        """获取轮询器"""
        return self._pollers.get(project_id)

    def is_polling(self, project_id: str) -> bool:
        """检查是否正在轮询"""
        poller = self._pollers.get(project_id)
        return poller.is_running if poller else False


# 全局实例
git_poller_manager = GitPollerManager()
