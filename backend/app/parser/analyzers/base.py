"""
分析器基类模块
定义代码分析的通用数据结构和抽象基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid


@dataclass
class CodeLocation:
    """代码位置"""
    file_path: str
    start_line: int
    end_line: int
    start_column: int = 0
    end_column: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "start_column": self.start_column,
            "end_column": self.end_column,
        }


@dataclass
class CodeEntity:
    """代码实体

    表示代码中的一个语法元素，如类、方法、字段等
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    qualified_name: str = ""  # 完全限定名，如 com.example.MyClass
    type: str = ""  # module, class, interface, enum, function, method, field, constructor
    file_path: str = ""
    start_line: int = 0
    end_line: int = 0
    start_column: int = 0
    end_column: int = 0
    modifiers: List[str] = field(default_factory=list)  # public, private, static 等
    annotations: List[str] = field(default_factory=list)  # @Override 等注解
    signature: str = ""  # 方法签名等
    docstring: str = ""  # 文档注释
    parent_id: Optional[str] = None  # 父实体 ID
    children: List['CodeEntity'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "type": self.type,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "start_column": self.start_column,
            "end_column": self.end_column,
            "modifiers": self.modifiers,
            "annotations": self.annotations,
            "signature": self.signature,
            "docstring": self.docstring,
            "parent_id": self.parent_id,
        }


@dataclass
class Dependency:
    """依赖关系

    表示代码实体之间的关系，如继承、实现、调用等
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""  # 源实体 ID
    target_id: str = ""  # 目标实体 ID
    target_name: str = ""  # 目标名称（用于后续解析）
    type: str = ""  # import, extend, implement, call, reference, use
    file_path: str = ""
    line: int = 0
    column: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "target_name": self.target_name,
            "type": self.type,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
        }


class BaseAnalyzer(ABC):
    """分析器基类

    提供代码分析的统一接口，各语言分析器需继承此类并实现抽象方法
    """

    def __init__(self, project_id: str):
        """初始化分析器

        Args:
            project_id: 项目标识
        """
        self.project_id = project_id
        self.entities: List[CodeEntity] = []
        self.dependencies: List[Dependency] = []
        self.entity_map: Dict[str, CodeEntity] = {}  # 名称 -> 实体映射
        self.entity_by_id: Dict[str, CodeEntity] = {}  # ID -> 实体映射

    @abstractmethod
    def get_language(self) -> str:
        """返回支持的语言

        Returns:
            语言名称，如 'java', 'typescript'
        """
        pass

    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """返回支持的文件扩展名

        Returns:
            文件扩展名列表，如 ['.java']
        """
        pass

    @abstractmethod
    def analyze_file(self, file_path: str, source_code: str) -> None:
        """分析单个文件

        Args:
            file_path: 文件路径
            source_code: 源代码内容
        """
        pass

    def analyze_project(self, project_path: str) -> None:
        """分析整个项目

        Args:
            project_path: 项目根目录路径
        """
        project = Path(project_path)

        # 需要跳过的目录
        skip_dirs = ["node_modules", "target", ".git", "dist", "build",
                     "__pycache__", ".idea", ".vscode", "venv", ".venv"]

        for ext in self.get_file_extensions():
            for file_path in project.rglob(f"*{ext}"):
                # 跳过忽略目录
                if any(skip in str(file_path) for skip in skip_dirs):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        source_code = f.read()
                    self.analyze_file(str(file_path), source_code)
                except Exception as e:
                    # 记录错误但继续处理其他文件
                    print(f"分析文件失败 {file_path}: {e}")

    def add_entity(self, entity: CodeEntity) -> None:
        """添加代码实体

        Args:
            entity: 代码实体
        """
        self.entities.append(entity)
        self.entity_by_id[entity.id] = entity
        if entity.qualified_name:
            self.entity_map[entity.qualified_name] = entity

    def add_dependency(self, dependency: Dependency) -> None:
        """添加依赖关系

        Args:
            dependency: 依赖关系
        """
        self.dependencies.append(dependency)

    def get_entity_by_name(self, name: str) -> Optional[CodeEntity]:
        """根据名称查找实体

        Args:
            name: 实体名称

        Returns:
            匹配的实体，未找到返回 None
        """
        return self.entity_map.get(name)

    def get_entity_by_id(self, entity_id: str) -> Optional[CodeEntity]:
        """根据 ID 查找实体

        Args:
            entity_id: 实体 ID

        Returns:
            匹配的实体，未找到返回 None
        """
        return self.entity_by_id.get(entity_id)

    def link_dependencies(self) -> None:
        """链接依赖关系

        将依赖中的 target_name 映射到 target_id
        对于未找到的目标，创建虚拟外部实体
        """
        external_entities = {}  # target_name -> entity_id

        for dep in self.dependencies:
            if not dep.target_id and dep.target_name:
                # 尝试通过名称查找目标实体
                target_entity = self.entity_map.get(dep.target_name)
                if target_entity:
                    dep.target_id = target_entity.id
                else:
                    # 创建虚拟外部实体
                    if dep.target_name not in external_entities:
                        external_entity = CodeEntity(
                            name=dep.target_name.split('.')[-1] if '.' in dep.target_name else dep.target_name,
                            qualified_name=dep.target_name,
                            type="external",
                            file_path="",
                            start_line=0,
                            end_line=0
                        )
                        self.add_entity(external_entity)
                        external_entities[dep.target_name] = external_entity.id

                    dep.target_id = external_entities[dep.target_name]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            包含 entities 和 dependencies 的字典
        """
        return {
            "entities": [e.to_dict() for e in self.entities],
            "dependencies": [d.to_dict() for d in self.dependencies],
            "language": self.get_language(),
            "project_id": self.project_id,
        }

    def clear(self) -> None:
        """清空分析结果"""
        self.entities.clear()
        self.dependencies.clear()
        self.entity_map.clear()
        self.entity_by_id.clear()
