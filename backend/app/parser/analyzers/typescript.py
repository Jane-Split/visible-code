"""
TypeScript 代码分析器
基于正则表达式的轻量级 TypeScript/JavaScript 代码解析器
"""
from app.parser.analyzers.base import BaseAnalyzer, CodeEntity, Dependency
from typing import List, Optional, Tuple
import re
import os


class TypeScriptAnalyzer(BaseAnalyzer):
    """TypeScript 代码分析器

    使用正则表达式解析 TypeScript 代码，提取类、接口、函数等代码实体
    """

    # 修饰符关键词
    MODIFIERS = {
        "public", "private", "protected", "readonly", "static",
        "abstract", "override", "declare", "export", "async"
    }

    # 类声明模式
    CLASS_PATTERN = re.compile(
        r'(export\s+)?'  # 导出
        r'(abstract\s+)?'  # 抽象
        r'class\s+'  # class 关键字
        r'(\w+)'  # 类名
        r'(?:<[\w,\s]+>)?'  # 泛型参数
        r'(?:\s+extends\s+([\w.<>]+?))?'  # 父类
        r'(?:\s+implements\s+([\w.,\s<>]+?))?'  # 实现的接口
        r'\s*[{]',
        re.MULTILINE
    )

    # 接口声明模式
    INTERFACE_PATTERN = re.compile(
        r'(export\s+)?'  # 导出
        r'interface\s+'  # interface 关键字
        r'(\w+)'  # 接口名
        r'(?:<[\w,\s]+>)?'  # 泛型参数
        r'(?:\s+extends\s+([\w.,\s<>]+?))?'  # 继承的接口
        r'\s*[{]',
        re.MULTILINE
    )

    # 类型别名模式
    TYPE_ALIAS_PATTERN = re.compile(
        r'(export\s+)?'  # 导出
        r'type\s+'  # type 关键字
        r'(\w+)'  # 类型别名
        r'(?:<[\w,\s]+>)?'  # 泛型参数
        r'\s*=\s*',
        re.MULTILINE
    )

    # 函数声明模式
    FUNCTION_PATTERN = re.compile(
        r'^(export\s+)?'  # 导出
        r'(async\s+)?'  # 异步
        r'(?:declare\s+)?'  # 声明
        r'function\s+'  # function 关键字
        r'(\w+)'  # 函数名
        r'(?:<[\w,\s]+>)?'  # 泛型参数
        r'\s*\([^)]*\)',  # 参数列表
        re.MULTILINE
    )

    # 箭头函数模式
    ARROW_FUNCTION_PATTERN = re.compile(
        r'^(export\s+)?'  # 导出
        r'(?:const|let|var)\s+'  # 变量声明
        r'(\w+)\s*'  # 变量名
        r'=\s*'  # 等号
        r'(?:async\s+)?'  # 异步
        r'(?:<[\w,\s]+>)?'  # 泛型参数
        r'\([^)]*\)'  # 参数
        r'\s*[=>]',  # 箭头
        re.MULTILINE
    )

    # 方法声明模式
    METHOD_PATTERN = re.compile(
        r'^\s+'  # 缩进
        r'((?:\w+\s+)*?)'  # 修饰符
        r'((?:\w+|<[\w,\s]+>)\s+)?'  # 返回类型
        r'(\w+)\s*'  # 方法名
        r'\([^)]*\)\s*'  # 参数
        r'(?::\s*\w+)?'  # 类型标注
        r'\s*[{=]',  # 函数体开始
        re.MULTILINE
    )

    # 字段声明模式
    FIELD_PATTERN = re.compile(
        r'^\s+'  # 缩进
        r'((?:\w+\s+)*?)'  # 修饰符
        r'(\w+)\s*'  # 字段名
        r'(?::\s*([\w<>\[\]|\s]+?))?'  # 类型
        r'\s*(?:=|;)',  # 赋值或声明结束
        re.MULTILINE
    )

    def get_language(self) -> str:
        """返回支持的语言"""
        return "typescript"

    def get_file_extensions(self) -> List[str]:
        """返回支持的文件扩展名"""
        return [".ts", ".tsx"]

    def analyze_file(self, file_path: str, source_code: str) -> None:
        """分析 TypeScript 文件

        Args:
            file_path: 文件路径
            source_code: 源代码
        """
        try:
            # 获取模块名
            module_name = self._get_module_name(file_path)

            # 提取导入声明
            self._extract_imports(source_code, file_path)

            # 提取类型别名
            self._extract_type_aliases(source_code, module_name, file_path)

            # 提取接口
            self._extract_interfaces(source_code, module_name, file_path)

            # 提取类
            self._extract_classes(source_code, module_name, file_path)

            # 提取函数
            self._extract_functions(source_code, module_name, file_path)

        except Exception as e:
            print(f"分析TypeScript文件失败 {file_path}: {e}")

    def _get_module_name(self, file_path: str) -> str:
        """获取模块名"""
        base = os.path.basename(file_path)
        name = os.path.splitext(base)[0]
        # 处理 index 文件
        if name == 'index':
            parent = os.path.basename(os.path.dirname(file_path))
            return parent
        return name

    def _extract_imports(self, source_code: str, file_path: str) -> None:
        """提取导入声明"""
        import_pattern = re.compile(
            r"import\s+(?:(?:(\w+)\s*,\s*)?(\{[^}]+\})|(\w+))"  # named imports / default import
            r"\s+from\s+['\"]([^'\"]+)['\"]",  # from path
            re.MULTILINE
        )

        # 为当前文件创建一个模块实体作为 import 的 source
        module_name = self._get_module_name(file_path)
        module_entity = None

        # 检查是否已存在该文件的模块实体
        for entity in self.entities:
            if entity.file_path == file_path and entity.type == "module":
                module_entity = entity
                break

        # 如果不存在，创建模块实体
        if not module_entity:
            module_entity = CodeEntity(
                name=module_name,
                qualified_name=module_name,
                type="module",
                file_path=file_path,
                start_line=1,
                end_line=source_code.count('\n') + 1
            )
            self.add_entity(module_entity)

        for match in import_pattern.finditer(source_code):
            imported_path = match.group(4)
            line = source_code[:match.start()].count('\n') + 1

            self.dependencies.append(Dependency(
                source_id=module_entity.id,  # 设置 source_id 为模块实体
                target_name=imported_path,
                type="import",
                file_path=file_path,
                line=line
            ))

    def _extract_type_aliases(
        self,
        source_code: str,
        module_name: str,
        file_path: str
    ) -> None:
        """提取类型别名"""
        for match in self.TYPE_ALIAS_PATTERN.finditer(source_code):
            export_keyword = match.group(1)
            type_name = match.group(2)
            line = source_code[:match.start()].count('\n') + 1

            qualified_name = f"{module_name}.{type_name}"

            entity = CodeEntity(
                name=type_name,
                qualified_name=qualified_name,
                type="type_alias",
                file_path=file_path,
                start_line=line,
                end_line=line,
                modifiers=["export"] if export_keyword else []
            )
            self.add_entity(entity)

    def _extract_interfaces(
        self,
        source_code: str,
        module_name: str,
        file_path: str
    ) -> None:
        """提取接口声明"""
        for match in self.INTERFACE_PATTERN.finditer(source_code):
            export_keyword = match.group(1)
            interface_name = match.group(2)
            extends_clause = match.group(3)
            line = source_code[:match.start()].count('\n') + 1

            # 查找接口结束位置
            brace_count = 0
            end_pos = match.end()
            in_interface = False

            for i, char in enumerate(source_code[match.start():]):
                if char == '{':
                    brace_count += 1
                    in_interface = True
                elif char == '}':
                    brace_count -= 1
                    if in_interface and brace_count == 0:
                        end_pos = match.start() + i + 1
                        break

            qualified_name = f"{module_name}.{interface_name}"
            modifiers = ["export"] if export_keyword else []

            entity = CodeEntity(
                name=interface_name,
                qualified_name=qualified_name,
                type="interface",
                file_path=file_path,
                start_line=line,
                end_line=source_code[:end_pos].count('\n') + 1,
                modifiers=modifiers
            )
            self.add_entity(entity)

            # 添加 extends 依赖
            if extends_clause:
                for iface in extends_clause.split(','):
                    iface = iface.strip()
                    if iface:
                        self.dependencies.append(Dependency(
                            source_id=entity.id,
                            target_name=iface,
                            type="extend",
                            file_path=file_path,
                            line=line
                        ))

    def _extract_classes(
        self,
        source_code: str,
        module_name: str,
        file_path: str
    ) -> None:
        """提取类声明"""
        for match in self.CLASS_PATTERN.finditer(source_code):
            export_keyword = match.group(1)
            abstract_keyword = match.group(2)
            class_name = match.group(3)
            extends_clause = match.group(4)
            implements_clause = match.group(5)
            line = source_code[:match.start()].count('\n') + 1

            # 查找类结束位置
            brace_count = 0
            end_pos = match.end()
            in_class = False

            for i, char in enumerate(source_code[match.start():]):
                if char == '{':
                    brace_count += 1
                    in_class = True
                elif char == '}':
                    brace_count -= 1
                    if in_class and brace_count == 0:
                        end_pos = match.start() + i + 1
                        break

            qualified_name = f"{module_name}.{class_name}"
            modifiers = []
            if export_keyword:
                modifiers.append("export")
            if abstract_keyword:
                modifiers.append("abstract")

            entity = CodeEntity(
                name=class_name,
                qualified_name=qualified_name,
                type="class",
                file_path=file_path,
                start_line=line,
                end_line=source_code[:end_pos].count('\n') + 1,
                modifiers=modifiers
            )
            self.add_entity(entity)

            # 添加 extends 依赖
            if extends_clause:
                extends_clause = extends_clause.strip()
                if extends_clause:
                    self.dependencies.append(Dependency(
                        source_id=entity.id,
                        target_name=extends_clause,
                        type="extend",
                        file_path=file_path,
                        line=line
                    ))

            # 添加 implements 依赖
            if implements_clause:
                for iface in implements_clause.split(','):
                    iface = iface.strip()
                    if iface:
                        self.dependencies.append(Dependency(
                            source_id=entity.id,
                            target_name=iface,
                            type="implement",
                            file_path=file_path,
                            line=line
                        ))

            # 解析类成员
            self._parse_class_members(entity, source_code[match.start():end_pos], file_path)

    def _parse_class_members(
        self,
        parent_entity: CodeEntity,
        class_body: str,
        file_path: str
    ) -> None:
        """解析类成员"""
        lines = class_body.split('\n')
        base_line = parent_entity.start_line

        for i, line in enumerate(lines):
            original_line = line
            stripped = line.strip()

            # 跳过空行和注释
            if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
                continue

            # 跳过类声明行和结束大括号
            if 'class ' in stripped or 'interface ' in stripped or stripped == '}' or stripped == '};':
                continue

            # 解析方法 - 支持多种格式
            # 格式1: public getUsers(): User[] {
            # 格式2: public getUsers() {
            # 格式3: private users: User[] = [];
            method_match = re.match(
                r'^'  # 行首
                r'((?:\w+\s+)*?)'  # 修饰符 (可选)
                r'([\w<>\[\]]+)?\s*'  # 返回类型 (可选)
                r'(\w+)\s*'  # 方法名
                r'\([^)]*\)\s*'  # 参数
                r'(?::\s*[\w<>\[\]]+)?'  # TypeScript 返回类型标注
                r'\s*([{=])',  # 函数体开始或赋值
                stripped
            )

            if method_match:
                modifiers_str = method_match.group(1) or ""
                return_type = method_match.group(2) or "void"
                method_name = method_match.group(3)
                brace_or_equals = method_match.group(4)

                # 跳过关键字
                if method_name in ['if', 'for', 'while', 'switch', 'catch', 'else', 'do', 'constructor']:
                    continue

                # 过滤有效的修饰符
                all_modifiers = ["public", "private", "protected", "readonly", "static", "abstract", "override", "declare", "export", "async"]
                modifiers = [m for m in all_modifiers if m in modifiers_str]

                current_line = base_line + class_body[:class_body.find(original_line)].count('\n') + i + 1

                # 确定是方法还是属性
                if brace_or_equals == '{':
                    # 方法
                    entity = CodeEntity(
                        name=method_name,
                        qualified_name=f"{parent_entity.qualified_name}.{method_name}",
                        type="method",
                        file_path=file_path,
                        start_line=current_line,
                        end_line=current_line,
                        modifiers=modifiers,
                        signature=f"{method_name}()",
                        parent_id=parent_entity.id
                    )
                    self.add_entity(entity)
                else:
                    # 这是箭头函数或属性赋值，跳过
                    pass
                continue

            # 解析属性/字段
            field_match = re.match(
                r'^'  # 行首
                r'((?:\w+\s+)*?)'  # 修饰符 (可选)
                r'(\w+)\s*'  # 字段名
                r'(?::\s*([\w<>\[\]|\s]+?))?'  # 类型 (可选)
                r'\s*(?:=|;)',  # 赋值或声明结束
                stripped
            )

            if field_match:
                modifiers_str = field_match.group(1) or ""
                field_name = field_match.group(2)
                field_type = field_match.group(3) or "any"

                # 过滤有效的修饰符
                all_modifiers = ["public", "private", "protected", "readonly", "static", "abstract", "override"]
                modifiers = [m for m in all_modifiers if m in modifiers_str]

                current_line = base_line + class_body[:class_body.find(original_line)].count('\n') + i + 1

                # 跳过方法（方法名后面有括号）
                if '(' not in field_name and field_name[0].islower():
                    entity = CodeEntity(
                        name=field_name,
                        qualified_name=f"{parent_entity.qualified_name}.{field_name}",
                        type="field",
                        file_path=file_path,
                        start_line=current_line,
                        end_line=current_line,
                        modifiers=modifiers,
                        signature=field_type,
                        parent_id=parent_entity.id
                    )
                    self.add_entity(entity)

    def _extract_functions(
        self,
        source_code: str,
        module_name: str,
        file_path: str
    ) -> None:
        """提取函数声明"""
        for match in self.FUNCTION_PATTERN.finditer(source_code):
            export_keyword = match.group(1)
            async_keyword = match.group(2)
            function_name = match.group(3)
            line = source_code[:match.start()].count('\n') + 1

            qualified_name = f"{module_name}.{function_name}"
            modifiers = []
            if export_keyword:
                modifiers.append("export")
            if async_keyword:
                modifiers.append("async")

            entity = CodeEntity(
                name=function_name,
                qualified_name=qualified_name,
                type="function",
                file_path=file_path,
                start_line=line,
                end_line=line,
                modifiers=modifiers
            )
            self.add_entity(entity)

    def _extract_arrow_functions(
        self,
        source_code: str,
        module_name: str,
        file_path: str
    ) -> None:
        """提取箭头函数"""
        for match in self.ARROW_FUNCTION_PATTERN.finditer(source_code):
            export_keyword = match.group(1)
            function_name = match.group(2)
            line = source_code[:match.start()].count('\n') + 1

            qualified_name = f"{module_name}.{function_name}"
            modifiers = []
            if export_keyword:
                modifiers.append("export")

            entity = CodeEntity(
                name=function_name,
                qualified_name=qualified_name,
                type="function",
                file_path=file_path,
                start_line=line,
                end_line=line,
                modifiers=modifiers
            )
            self.add_entity(entity)
