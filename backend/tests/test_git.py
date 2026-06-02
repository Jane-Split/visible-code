import pytest
import tempfile
import shutil
from pathlib import Path
from app.core.git import GitOperator, GitOperationError

@pytest.fixture
def temp_repo():
    """创建临时仓库用于测试"""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "test_repo"
    repo_path.mkdir()

    # 初始化仓库
    import subprocess
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_path, check=True)

    # 创建初始提交
    readme = repo_path / "README.md"
    readme.write_text("# Test")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)

    yield repo_path

    shutil.rmtree(temp_dir)

def test_git_operator_init():
    """测试 GitOperator 初始化"""
    with tempfile.TemporaryDirectory() as temp_dir:
        op = GitOperator(temp_dir)
        assert op.repos_path.exists()

def test_get_current_commit(temp_repo):
    """测试获取当前 commit"""
    op = GitOperator(str(temp_repo.parent))
    commit = op.get_current_commit(str(temp_repo))
    assert len(commit) == 40  # SHA-1 hash length

def test_list_branches(temp_repo):
    """测试列出分支"""
    op = GitOperator(str(temp_repo.parent))
    branches, current = op.list_branches(str(temp_repo))
    assert "main" in branches or "master" in branches
    assert current in ["main", "master", ""]

def test_get_changed_files(temp_repo):
    """测试获取变更文件"""
    import subprocess

    # 添加新文件
    new_file = temp_repo / "new_file.txt"
    new_file.write_text("new content")
    subprocess.run(["git", "add", "."], cwd=temp_repo, check=True)
    subprocess.run(["git", "commit", "-m", "Add new file"], cwd=temp_repo, check=True, capture_output=True)

    op = GitOperator(str(temp_repo.parent))
    first_commit = op.get_current_commit(str(temp_repo))

    # 再添加一个文件
    another = temp_repo / "another.txt"
    another.write_text("content")
    subprocess.run(["git", "add", "."], cwd=temp_repo, check=True)
    subprocess.run(["git", "commit", "-m", "Add another"], cwd=temp_repo, check=True, capture_output=True)

    second_commit = op.get_current_commit(str(temp_repo))
    changes = op.get_changed_files(str(temp_repo), first_commit, second_commit)

    assert len(changes) >= 1
    assert any("another.txt" in c[0] for c in changes)
