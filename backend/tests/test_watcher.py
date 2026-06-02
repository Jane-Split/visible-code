import pytest
import asyncio
from pathlib import Path
import tempfile
import time
from app.watcher.file_watcher import FileWatcher, CodeFileEventHandler
from app.watcher.git_poller import GitPoller


def test_file_watcher_init():
    """测试文件监听器初始化"""
    watcher = FileWatcher()
    assert watcher is not None


def test_code_file_event_handler_extensions():
    """测试支持的扩展名"""
    handler = CodeFileEventHandler("test-project", lambda x: None)

    # 测试支持的扩展名
    assert handler._should_process("test.java")
    assert handler._should_process("test.ts")
    assert handler._should_process("test.py")
    assert handler._should_process("test.go")

    # 测试不支持的扩展名
    assert not handler._should_process("test.txt")
    assert not handler._should_process("test.exe")


def test_code_file_event_handler_ignored_dirs():
    """测试忽略的目录"""
    handler = CodeFileEventHandler("test-project", lambda x: None)

    # 测试忽略的目录
    assert not handler._should_process("/path/to/node_modules/test.js")
    assert not handler._should_process("/path/to/target/Main.java")
    assert not handler._should_process("/path/to/.git/config")

    # 测试正常路径
    assert handler._should_process("/path/to/src/Main.java")


@pytest.mark.asyncio
async def test_git_poller_init():
    """测试 Git 轮询器初始化"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建临时 Git 仓库
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        import subprocess
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_path, check=True)

        # 创建初始提交
        readme = repo_path / "README.md"
        readme.write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=repo_path, check=True)

        # 创建轮询器
        poller = GitPoller(
            project_id="test-project",
            repo_path=str(repo_path),
            interval=1
        )

        assert poller.project_id == "test-project"
        assert poller.interval == 1
        assert not poller.is_running
