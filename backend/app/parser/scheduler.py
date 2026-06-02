"""
解析调度器模块
提供代码解析的统一入口和调度功能
"""
from pathlib import Path
from typing import List, Dict, Optional, Any, Type
import asyncio
import logging

from app.parser.analyzers.base import BaseAnalyzer
from app.parser.analyzers.java import JavaAnalyzer
from app.parser.analyzers.typescript import TypeScriptAnalyzer

logger = logging.getLogger(__name__)


class ParseScheduler:
    """解析调度器

    负责管理各语言分析器，提供文件解析和项目解析的统一接口
    """

    # 分析器映射表
    ANALYZER_MAP: Dict[str, Type[BaseAnalyzer]] = {
        "java": JavaAnalyzer,
        "typescript": TypeScriptAnalyzer,
        "javascript": TypeScriptAnalyzer,  # JavaScript 使用 TypeScript 分析器
        "tsx": TypeScriptAnalyzer,
        "jsx": TypeScriptAnalyzer,
    }

    # 文件扩展名到语言的映射
    EXTENSION_TO_LANGUAGE: Dict[str, str] = {
        ".java": "java",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
    }

    # 需要跳过的目录
    SKIP_DIRECTORIES: List[str] = [
        "node_modules",
        "target",
        ".git",
        "dist",
        "build",
        "__pycache__",
        ".idea",
        ".vscode",
        "venv",
        ".venv",
        "coverage",
        ".next",
        ".nuxt",
        "bin",
        "obj",
    ]

    def __init__(self):
        """初始化调度器"""
        self._analyzer_instances: Dict[str, BaseAnalyzer] = {}

    def get_analyzer(self, language: str) -> Optional[Type[BaseAnalyzer]]:
        """获取分析器类

        Args:
            language: 语言名称

        Returns:
            分析器类，未注册返回 None
        """
        return self.ANALYZER_MAP.get(language.lower())

    def get_analyzer_instance(self, project_id: str, language: str) -> Optional[BaseAnalyzer]:
        """获取分析器实例

        Args:
            project_id: 项目 ID
            language: 语言名称

        Returns:
            分析器实例
        """
        analyzer_class = self.get_analyzer(language)
        if analyzer_class:
            return analyzer_class(project_id)
        return None

    def detect_language(self, file_path: str) -> Optional[str]:
        """根据文件扩展名检测语言

        Args:
            file_path: 文件路径

        Returns:
            语言名称，未知返回 None
        """
        ext = Path(file_path).suffix.lower()
        return self.EXTENSION_TO_LANGUAGE.get(ext)

    def is_skip_directory(self, path: str) -> bool:
        """检查路径是否在跳过目录中

        Args:
            path: 文件或目录路径

        Returns:
            是否跳过
        """
        path_parts = Path(path).parts
        return any(skip in path_parts for skip in self.SKIP_DIRECTORIES)

    async def parse_file(
        self,
        project_id: str,
        file_path: str,
        source_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """解析单个文件

        Args:
            project_id: 项目 ID
            file_path: 文件路径
            source_code: 源代码内容，如果为 None 则从文件读取

        Returns:
            解析结果字典，包含 entities 和 dependencies
        """
        language = self.detect_language(file_path)
        if not language:
            return {
                "error": f"不支持的文件类型: {file_path}",
                "entities": [],
                "dependencies": []
            }

        analyzer = self.get_analyzer_instance(project_id, language)
        if not analyzer:
            return {
                "error": f"未注册的分析器: {language}",
                "entities": [],
                "dependencies": []
            }

        try:
            # 如果没有提供源代码，从文件读取
            if source_code is None:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    source_code = f.read()

            # 分析文件
            analyzer.analyze_file(file_path, source_code)

            # 获取结果
            result = analyzer.to_dict()

            # 链接依赖关系
            analyzer.link_dependencies()

            return result

        except Exception as e:
            logger.error(f"解析文件失败 {file_path}: {e}")
            return {
                "error": str(e),
                "entities": [],
                "dependencies": []
            }

    async def parse_project(
        self,
        project_id: str,
        project_path: str,
        languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """解析整个项目

        Args:
            project_id: 项目 ID
            project_path: 项目根目录路径
            languages: 要解析的语言列表，None 表示所有语言

        Returns:
            解析结果汇总
        """
        results = {
            "entities": [],
            "dependencies": [],
            "errors": [],
            "file_count": 0,
            "language": "mixed"
        }

        languages = languages or list(self.ANALYZER_MAP.keys())
        project = Path(project_path)

        if not project.exists():
            results["errors"].append({"error": f"项目路径不存在: {project_path}"})
            return results

        # 按语言分组解析
        for ext, lang in self.EXTENSION_TO_LANGUAGE.items():
            if lang not in languages:
                continue

            for file_path in project.rglob(f"*{ext}"):
                # 跳过忽略目录
                if self.is_skip_directory(str(file_path)):
                    continue

                results["file_count"] += 1

                result = await self.parse_file(project_id, str(file_path))

                if "error" in result and result["error"]:
                    results["errors"].append({
                        "file": str(file_path),
                        "error": result["error"]
                    })
                else:
                    results["entities"].extend(result.get("entities", []))
                    results["dependencies"].extend(result.get("dependencies", []))

        return results

    def parse_project_sync(
        self,
        project_id: str,
        project_path: str,
        languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """同步解析整个项目

        Args:
            project_id: 项目 ID
            project_path: 项目根目录路径
            languages: 要解析的语言列表

        Returns:
            解析结果汇总
        """
        results = {
            "entities": [],
            "dependencies": [],
            "errors": [],
            "file_count": 0,
            "language": "mixed"
        }

        languages = languages or list(self.ANALYZER_MAP.keys())
        project = Path(project_path)

        if not project.exists():
            results["errors"].append({"error": f"项目路径不存在: {project_path}"})
            return results

        # 按语言分组解析
        for ext, lang in self.EXTENSION_TO_LANGUAGE.items():
            if lang not in languages:
                continue

            for file_path in project.rglob(f"*{ext}"):
                # 跳过忽略目录
                if self.is_skip_directory(str(file_path)):
                    continue

                results["file_count"] += 1

                # 同步调用
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self.parse_file(project_id, str(file_path))
                    )
                finally:
                    loop.close()

                if "error" in result and result["error"]:
                    results["errors"].append({
                        "file": str(file_path),
                        "error": result["error"]
                    })
                else:
                    results["entities"].extend(result.get("entities", []))
                    results["dependencies"].extend(result.get("dependencies", []))

        return results

    def get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名

        Returns:
            扩展名列表
        """
        return list(self.EXTENSION_TO_LANGUAGE.keys())

    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表

        Returns:
            语言列表
        """
        return list(set(self.EXTENSION_TO_LANGUAGE.values()))


# 全局实例
parse_scheduler = ParseScheduler()
