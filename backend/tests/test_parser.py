"""
代码解析器测试
测试 Java 和 TypeScript 分析器的功能
"""
import pytest
from pathlib import Path
import tempfile
import os
import shutil

from app.parser.scheduler import ParseScheduler
from app.parser.analyzers.java import JavaAnalyzer
from app.parser.analyzers.typescript import TypeScriptAnalyzer
from app.parser.analyzers.base import CodeEntity, Dependency


@pytest.fixture
def temp_java_project():
    """创建临时 Java 项目"""
    temp_dir = tempfile.mkdtemp()
    project_dir = Path(temp_dir) / "java_project"
    project_dir.mkdir()

    # 创建包目录
    (project_dir / "com" / "example").mkdir(parents=True)
    service_dir = project_dir / "com" / "example" / "service"
    service_dir.mkdir(parents=True)

    # 创建主类
    main_content = """
package com.example;

public class Main {
    private String name;
    private int age;

    public Main() {
    }

    public Main(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return "Main{name='" + name + "'}";
    }

    public void sayHello() {
        System.out.println("Hello");
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
"""
    (project_dir / "com" / "example" / "Main.java").write_text(main_content)

    # 创建服务类
    service_content = """
package com.example.service;

import com.example.Main;

public class UserService {
    private Main main;
    private String userName;

    public void create() {
        main = new Main();
    }

    public String getUserName() {
        return userName;
    }
}
"""
    (project_dir / "com" / "example" / "service" / "UserService.java").write_text(service_content)

    # 创建接口
    interface_content = """
package com.example.service;

public interface UserRepository {
    void save(String user);

    String findById(int id);
}
"""
    (project_dir / "com" / "example" / "service" / "UserRepository.java").write_text(interface_content)

    yield str(project_dir)

    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_typescript_project():
    """创建临时 TypeScript 项目"""
    temp_dir = tempfile.mkdtemp()
    project_dir = Path(temp_dir) / "ts_project"
    project_dir.mkdir()

    # 创建服务类
    service_content = """
export interface User {
    id: number;
    name: string;
    email?: string;
}

export class UserService {
    private users: User[] = [];
    private name: string;

    constructor() {
        this.name = "UserService";
    }

    public getUsers(): User[] {
        return this.users;
    }

    public addUser(user: User): void {
        this.users.push(user);
    }

    public getUserById(id: number): User | undefined {
        return this.users.find(u => u.id === id);
    }
}

export type UserStatus = 'active' | 'inactive' | 'deleted';
"""
    (project_dir / "UserService.ts").write_text(service_content)

    # 创建另一个文件
    utils_content = """
export class StringUtils {
    public static capitalize(str: string): string {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

export function formatDate(date: Date): string {
    return date.toISOString();
}
"""
    (project_dir / "utils.ts").write_text(utils_content)

    yield str(project_dir)

    shutil.rmtree(temp_dir)


class TestParseScheduler:
    """测试解析调度器"""

    def test_scheduler_init(self):
        """测试调度器初始化"""
        scheduler = ParseScheduler()
        assert scheduler is not None
        assert ".java" in scheduler.get_supported_extensions()
        assert ".ts" in scheduler.get_supported_extensions()

    def test_detect_language(self):
        """测试语言检测"""
        scheduler = ParseScheduler()
        assert scheduler.detect_language("test.java") == "java"
        assert scheduler.detect_language("test.ts") == "typescript"
        assert scheduler.detect_language("test.tsx") == "typescript"
        assert scheduler.detect_language("test.js") == "javascript"
        assert scheduler.detect_language("test.py") is None
        assert scheduler.detect_language("test.cpp") is None

    def test_get_analyzer(self):
        """测试获取分析器"""
        scheduler = ParseScheduler()
        java_analyzer = scheduler.get_analyzer("java")
        ts_analyzer = scheduler.get_analyzer("typescript")
        assert java_analyzer is not None
        assert ts_analyzer is not None
        assert java_analyzer == JavaAnalyzer
        assert ts_analyzer == TypeScriptAnalyzer

    def test_is_skip_directory(self):
        """测试跳过目录检测"""
        scheduler = ParseScheduler()
        assert scheduler.is_skip_directory("/path/node_modules/test.js")
        assert scheduler.is_skip_directory("/path/target/classes/Main.java")
        assert scheduler.is_skip_directory("/path/.git/config")
        assert not scheduler.is_skip_directory("/path/src/Main.java")


class TestJavaAnalyzer:
    """测试 Java 分析器"""

    def test_analyzer_language(self):
        """测试分析器语言标识"""
        analyzer = JavaAnalyzer("test-project")
        assert analyzer.get_language() == "java"
        assert ".java" in analyzer.get_file_extensions()

    def test_parse_simple_class(self):
        """测试解析简单类"""
        analyzer = JavaAnalyzer("test-project")

        source = """
public class SimpleClass {
    private String name;

    public String getName() {
        return name;
    }
}
"""
        analyzer.analyze_file("SimpleClass.java", source)

        entities = analyzer.entities
        assert len(entities) > 0

        # 检查类
        class_entities = [e for e in entities if e.type == "class"]
        assert len(class_entities) >= 1
        class_entity = class_entities[0]
        assert class_entity.name == "SimpleClass"

        # 检查方法
        method_entities = [e for e in entities if e.type == "method"]
        assert len(method_entities) >= 1

    def test_parse_package_class(self):
        """测试解析带包名的类"""
        analyzer = JavaAnalyzer("test-project")

        source = """
package com.example.service;

public class UserService {
    public void save() {}
}
"""
        analyzer.analyze_file("UserService.java", source)

        entities = analyzer.entities
        class_entities = [e for e in entities if e.type == "class"]
        assert len(class_entities) >= 1
        assert "UserService" in class_entities[0].name

    def test_parse_annotations(self):
        """测试解析注解"""
        analyzer = JavaAnalyzer("test-project")

        source = """
public class AnnotatedClass {
    @Override
    public String toString() {
        return "";
    }

    @Deprecated
    public void oldMethod() {}
}
"""
        analyzer.analyze_file("AnnotatedClass.java", source)

        entities = analyzer.entities
        override_methods = [e for e in entities if "@Override" in e.annotations]
        assert len(override_methods) >= 1

    def test_parse_imports(self):
        """测试解析导入语句"""
        analyzer = JavaAnalyzer("test-project")

        source = """
import java.util.List;
import java.util.ArrayList;
import com.example.Service;

public class Test {}
"""
        analyzer.analyze_file("Test.java", source)

        import_deps = [d for d in analyzer.dependencies if d.type == "import"]
        assert len(import_deps) >= 3

    def test_parse_project(self, temp_java_project):
        """测试解析整个项目"""
        analyzer = JavaAnalyzer("test-project")
        analyzer.analyze_project(temp_java_project)

        entities = analyzer.entities
        assert len(entities) > 0

        # 检查类名
        class_names = [e.name for e in entities if e.type == "class"]
        assert "Main" in class_names
        assert "UserService" in class_names


class TestTypeScriptAnalyzer:
    """测试 TypeScript 分析器"""

    def test_analyzer_language(self):
        """测试分析器语言标识"""
        analyzer = TypeScriptAnalyzer("test-project")
        assert analyzer.get_language() == "typescript"
        assert ".ts" in analyzer.get_file_extensions()
        assert ".tsx" in analyzer.get_file_extensions()

    def test_parse_interface(self):
        """测试解析接口"""
        analyzer = TypeScriptAnalyzer("test-project")

        source = """
export interface User {
    id: number;
    name: string;
}
"""
        analyzer.analyze_file("User.ts", source)

        entities = analyzer.entities
        interface_entities = [e for e in entities if e.type == "interface"]
        assert len(interface_entities) >= 1
        assert interface_entities[0].name == "User"

    def test_parse_class(self):
        """测试解析类"""
        analyzer = TypeScriptAnalyzer("test-project")

        source = """
export class UserService {
    private users: User[] = [];

    public getUsers(): User[] {
        return this.users;
    }
}
"""
        analyzer.analyze_file("UserService.ts", source)

        entities = analyzer.entities
        class_entities = [e for e in entities if e.type == "class"]
        assert len(class_entities) >= 1
        assert class_entities[0].name == "UserService"

        # 检查方法
        method_entities = [e for e in entities if e.type == "method"]
        assert len(method_entities) >= 1

    def test_parse_type_alias(self):
        """测试解析类型别名"""
        analyzer = TypeScriptAnalyzer("test-project")

        source = """
export type UserStatus = 'active' | 'inactive';

export type Callback = (data: string) => void;
"""
        analyzer.analyze_file("types.ts", source)

        entities = analyzer.entities
        type_aliases = [e for e in entities if e.type == "type_alias"]
        assert len(type_aliases) >= 2
        names = [e.name for e in type_aliases]
        assert "UserStatus" in names
        assert "Callback" in names

    def test_parse_project(self, temp_typescript_project):
        """测试解析整个项目"""
        analyzer = TypeScriptAnalyzer("test-project")
        analyzer.analyze_project(temp_typescript_project)

        entities = analyzer.entities
        assert len(entities) > 0

        # 检查类名
        class_names = [e.name for e in entities if e.type == "class"]
        assert "UserService" in class_names
        assert "StringUtils" in class_names


class TestCodeEntity:
    """测试代码实体"""

    def test_entity_creation(self):
        """测试实体创建"""
        entity = CodeEntity(
            name="TestClass",
            qualified_name="com.example.TestClass",
            type="class",
            file_path="/path/TestClass.java",
            start_line=10,
            end_line=50
        )
        assert entity.name == "TestClass"
        assert entity.type == "class"
        assert entity.start_line == 10
        assert entity.end_line == 50
        assert entity.id is not None

    def test_entity_to_dict(self):
        """测试实体转字典"""
        entity = CodeEntity(
            name="TestClass",
            qualified_name="com.example.TestClass",
            type="class"
        )
        d = entity.to_dict()
        assert d["name"] == "TestClass"
        assert d["type"] == "class"
        assert "id" in d


class TestDependency:
    """测试依赖关系"""

    def test_dependency_creation(self):
        """测试依赖创建"""
        dep = Dependency(
            source_id="source-123",
            target_id="target-456",
            type="extend",
            file_path="/path/Class.java",
            line=10
        )
        assert dep.source_id == "source-123"
        assert dep.target_id == "target-456"
        assert dep.type == "extend"

    def test_dependency_types(self):
        """测试依赖类型"""
        dep = Dependency(type="import")
        assert dep.type == "import"

        dep = Dependency(type="extend")
        assert dep.type == "extend"

        dep = Dependency(type="implement")
        assert dep.type == "implement"


class TestIntegration:
    """集成测试"""

    @pytest.mark.asyncio
    async def test_parse_file_via_scheduler(self):
        """通过调度器解析文件"""
        scheduler = ParseScheduler()

        result = await scheduler.parse_file(
            "test-project",
            "test.java",
            "public class Test {}"
        )

        assert "entities" in result
        assert "dependencies" in result

    def test_parse_java_project_via_scheduler(self, temp_java_project):
        """通过调度器解析 Java 项目"""
        scheduler = ParseScheduler()

        result = scheduler.parse_project_sync(
            "test-project",
            temp_java_project,
            languages=["java"]
        )

        assert result["file_count"] >= 3
        assert len(result["entities"]) > 0
        assert len(result["errors"]) == 0

    def test_parse_typescript_project_via_scheduler(self, temp_typescript_project):
        """通过调度器解析 TypeScript 项目"""
        scheduler = ParseScheduler()

        result = scheduler.parse_project_sync(
            "test-project",
            temp_typescript_project,
            languages=["typescript"]
        )

        assert result["file_count"] >= 2
        assert len(result["entities"]) > 0
        assert len(result["errors"]) == 0
