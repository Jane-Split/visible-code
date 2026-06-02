"""
Tree-sitter 管理器模块
提供 Tree-sitter 解析器的统一管理接口
"""
from pathlib import Path
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# 尝试导入 tree-sitter
try:
    from tree_sitter import Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    logger.warning("tree-sitter 未安装，将使用正则表达式解析器")


class TreeSitterManager:
    """Tree-sitter 管理器

    提供统一的语言解析接口，支持 tree-sitter 和轻量级正则解析两种模式。
    """

    _instance = None
    _parsers: Dict[str, Any] = {}
    _languages: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def is_available(self) -> bool:
        """检查 tree-sitter 是否可用"""
        return TREE_SITTER_AVAILABLE

    def get_language(self, language: str):
        """获取语言支持

        Args:
            language: 语言名称 (java, typescript, javascript, python, go)

        Returns:
            语言对象

        Raises:
            ValueError: 不支持的语言
            ImportError: 语言包未安装
        """
        if not TREE_SITTER_AVAILABLE:
            raise ImportError("tree-sitter 未安装")

        if language in self._languages:
            return self._languages[language]

        # 语言映射
        lang_map = {
            "java": "java",
            "typescript": "typescript",
            "javascript": "javascript",
            "tsx": "tsx",
            "jsx": "jsx",
            "python": "python",
            "go": "go",
        }

        ts_language = lang_map.get(language.lower())
        if not ts_language:
            raise ValueError(f"不支持的语言: {language}")

        try:
            # 动态导入语言库
            lang_module = __import__(f"tree_sitter_{ts_language}", fromlist=["language"])
            self._languages[language] = lang_module.language()
            return self._languages[language]
        except ImportError:
            logger.warning(f"Tree-sitter {ts_language} 语言包未安装")
            raise ImportError(f"请安装 tree-sitter-{ts_language}")

    def get_parser(self, language: str) -> Optional[Any]:
        """获取解析器

        Args:
            language: 语言名称

        Returns:
            Parser 对象，如果不可用则返回 None
        """
        if not TREE_SITTER_AVAILABLE:
            return None

        if language in self._parsers:
            return self._parsers[language]

        try:
            parser = Parser()
            lang = self.get_language(language)
            parser.set_language(lang)
            self._parsers[language] = parser
            return parser
        except Exception as e:
            logger.warning(f"获取解析器失败: {language} - {e}")
            return None

    def parse_file(self, file_path: str, language: str) -> Optional[Any]:
        """解析文件

        Args:
            file_path: 文件路径
            language: 语言名称

        Returns:
            解析树对象，解析失败返回 None
        """
        parser = self.get_parser(language)
        if parser is None:
            return None

        try:
            with open(file_path, "rb") as f:
                source_code = f.read()
            return parser.parse(source_code)
        except Exception as e:
            logger.error(f"解析文件失败: {file_path} - {e}")
            return None

    def parse_source(self, source_code: str, language: str) -> Optional[Any]:
        """解析源代码字符串

        Args:
            source_code: 源代码字符串
            language: 语言名称

        Returns:
            解析树对象，解析失败返回 None
        """
        parser = self.get_parser(language)
        if parser is None:
            return None

        try:
            return parser.parse(bytes(source_code, "utf8"))
        except Exception as e:
            logger.error(f"解析源代码失败: {e}")
            return None


# 全局实例
ts_manager = TreeSitterManager()
