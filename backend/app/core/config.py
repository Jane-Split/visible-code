import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/codeviz.db")

# 文件存储路径
REPOS_PATH = os.getenv("REPOS_PATH", str(BASE_DIR / "repos"))
DATA_PATH = os.getenv("DATA_PATH", str(BASE_DIR / "data"))

# 确保目录存在
Path(REPOS_PATH).mkdir(parents=True, exist_ok=True)
Path(DATA_PATH).mkdir(parents=True, exist_ok=True)

# API 配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Git 配置
GIT_DEFAULT_BRANCH = "main"
GIT_CLONE_DEPTH = 1  # shallow clone

# 解析配置
SUPPORTED_LANGUAGES = ["java", "typescript", "javascript", "python", "go"]
MAX_FILE_SIZE = 1024 * 1024  # 1MB
