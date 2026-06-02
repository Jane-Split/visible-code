"""Git 操作模块"""
import subprocess
from pathlib import Path
from typing import Optional
import shutil

class GitOperationError(Exception):
    """Git 操作异常"""
    pass

class GitOperator:
    """Git 操作工具类"""

    def __init__(self, repos_path: str):
        self.repos_path = Path(repos_path)
        self.repos_path.mkdir(parents=True, exist_ok=True)

    def verify_repository(self, url: str) -> bool:
        """验证 Git 仓库 URL 是否有效"""
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--heads", url],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0 and len(result.stdout.strip()) > 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def clone(self, url: str, project_id: str, branch: str = "main") -> str:
        """克隆 Git 仓库"""
        dest_path = self.repos_path / project_id

        try:
            # 使用 shallow clone
            subprocess.run(
                [
                    "git", "clone",
                    "--branch", branch,
                    "--depth", "1",
                    "--single-branch",
                    url,
                    str(dest_path)
                ],
                check=True,
                capture_output=True,
                timeout=300
            )
            return str(dest_path)
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"克隆失败: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise GitOperationError("克隆超时")

    def fetch(self, repo_path: str) -> None:
        """拉取远程更新"""
        try:
            subprocess.run(
                ["git", "fetch", "--all"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                timeout=60
            )
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"Fetch 失败: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise GitOperationError("Fetch 超时")

    def pull(self, repo_path: str) -> None:
        """拉取并合并更新"""
        try:
            subprocess.run(
                ["git", "pull", "origin", "HEAD"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                timeout=60
            )
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"Pull 失败: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise GitOperationError("Pull 超时")

    def checkout(self, repo_path: str, branch: str) -> None:
        """切换分支"""
        try:
            subprocess.run(
                ["git", "checkout", branch],
                cwd=repo_path,
                check=True,
                capture_output=True,
                timeout=30
            )
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"Checkout 失败: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise GitOperationError("Checkout 超时")

    def get_current_commit(self, repo_path: str) -> str:
        """获取当前 commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"获取 commit 失败: {e.stderr}")

    def get_branches(self, repo_path: str) -> list:
        """获取所有分支"""
        try:
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            branches = [b.strip().replace("* ", "") for b in result.stdout.strip().split("\n") if b.strip()]
            return branches
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"获取分支失败: {e.stderr}")

    def list_branches(self, repo_path: str) -> tuple:
        """列出所有分支并返回当前分支
        
        Returns:
            (branches_list, current_branch)
        """
        try:
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            branches = []
            current = ""
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith("* "):
                    current = line.replace("* ", "")
                    branches.append(current)
                else:
                    branches.append(line)
            return branches, current
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"获取分支失败: {e.stderr}")

    def get_changed_files(self, repo_path: str, from_commit: str, to_commit: str) -> list:
        """获取两个 commit 之间的变更文件列表
        
        Args:
            repo_path: 仓库路径
            from_commit: 起始 commit
            to_commit: 结束 commit
            
        Returns:
            [(file_path, change_type), ...] 变更文件列表
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-status", from_commit, to_commit],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            changes = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) >= 2:
                    change_type = parts[0][0]  # A, M, D, R, etc.
                    file_path = parts[1]
                    changes.append((file_path, change_type))
            return changes
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"获取变更文件失败: {e.stderr}")
