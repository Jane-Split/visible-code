"""
Java 代码分析器
基于正则表达式的轻量级 Java 代码解析器
"""
from app.parser.analyzers.base import BaseAnalyzer, CodeEntity, Dependency
from typing import List, Optional, Dict, Tuple
import re
import os


class JavaAnalyzer(BaseAnalyzer):
    """Java 代码分析器

    使用正则表达式解析 Java 代码，提取类、方法、字段等代码实体
    """

    # 修饰符关键词
    MODIFIERS = {
        "public", "private", "protected", "static", "final",
        "abstract", "synchronized", "volatile", "transient", "native",
        "strictfp", "transient"
    }

    # 注解模式
    ANNOTATION_PATTERN = re.compile(r'@(\w+(?:\([^)]*\))?)')

    # 类声明模式
    CLASS_PATTERN = re.compile(
        r'((?:@[\w]+\s*)*)?'  # 注解（可选）
        r'((?:public|private|protected|static|final|abstract|synchronized|strictfp)\s+)*'  # 修饰符
        r'(class|interface|enum)\s+'  # 类型
        r'(\w+)'  # 类名
        r'(?:\s+extends\s+([\w.]+))?'  # 父类
        r'(?:\s+implements\s+([\w.,\s]+))?'  # 实现的接口
        r'\s*\{',
        re.MULTILINE | re.DOTALL
    )

    # 方法声明模式
    METHOD_PATTERN = re.compile(
        r'^(\s*)'  # 缩进
        r'((?:@[\w]+\s*)*)?'  # 注解
        r'((?:public|private|protected|static|final|abstract|synchronized|native)\s+)*'  # 修饰符
        r'([\w.]+)\s+'  # 返回类型
        r'(\w+)\s*'  # 方法名
        r'\(([^)]*)\)'  # 参数列表
        r'\s*(?:throws\s+[\w.,\s]+)?'  # 异常声明
        r'\s*\{',
        re.MULTILINE
    )

    # 构造函数模式
    CONSTRUCTOR_PATTERN = re.compile(
        r'^(\s*)'  # 缩进
        r'((?:@[\w]+\s*)*)?'  # 注解
        r'((?:public|private|protected)\s+)*'  # 修饰符
        r'(\w+)\s*'  # 构造函数名
        r'\(([^)]*)\)'  # 参数列表
        r'\s*(?:throws\s+[\w.,\s]+)?'  # 异常声明
        r'\s*\{',
        re.MULTILINE
    )

    # 字段声明模式
    FIELD_PATTERN = re.compile(
        r'^(\s*)'  # 缩进
        r'((?:@[\w]+\s*)*)?'  # 注解
        r'((?:public|private|protected|static|final|volatile|transient)\s+)*'  # 修饰符
        r'([\w.]+)\s+'  # 类型
        r'([\w,\s]+)'  # 字段名（可能有多个，用逗号分隔）
        r'\s*;',
        re.MULTILINE
    )

    # 导入声明模式
    IMPORT_PATTERN = re.compile(r'import\s+(?:static\s+)?([\w.*]+);')

    def get_language(self) -> str:
        """返回支持的语言"""
        return "java"

    def get_file_extensions(self) -> List[str]:
        """返回支持的文件扩展名"""
        return [".java"]

    def analyze_file(self, file_path: str, source_code: str) -> None:
        """分析 Java 文件

        Args:
            file_path: 文件路径
            source_code: 源代码
        """
        try:
            # 获取包名
            package_name = self._extract_package(source_code)

            # 获取导入声明
            imports = self._extract_imports(source_code, file_path)

            # 获取类列表及层级结构
            classes = self._extract_classes(source_code, package_name, file_path)

            # 解析每个类
            for class_entity, class_body in classes:
                self._parse_class(class_entity, class_body, source_code, file_path, imports)

        except Exception as e:
            print(f"分析Java文件失败 {file_path}: {e}")

    def _extract_package(self, source_code: str) -> str:
        """提取包名"""
        match = re.search(r'package\s+([\w.]+);', source_code)
        return match.group(1) if match else ""

    def _extract_imports(self, source_code: str, file_path: str) -> List[str]:
        """提取导入声明"""
        imports = []

        # 为当前文件创建一个模块实体作为 import 的 source
        package_name = self._extract_package(source_code)
        class_match = re.search(r'(class|interface|enum)\s+(\w+)', source_code)
        if class_match:
            class_name = class_match.group(2)
            module_name = f"{package_name}.{class_name}" if package_name else class_name
        else:
            module_name = os.path.basename(file_path).replace('.java', '')

        # 检查是否已存在该文件的模块实体
        module_entity = None
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

        for match in self.IMPORT_PATTERN.finditer(source_code):
            imported = match.group(1)
            imports.append(imported)

            # 添加 import 依赖，设置 source_id
            self.dependencies.append(Dependency(
                source_id=module_entity.id,
                target_name=imported,
                type="import",
                file_path=file_path,
                line=source_code[:match.start()].count('\n') + 1
            ))
        return imports

    def _extract_classes(self, source_code: str, package: str, file_path: str) -> List[Tuple[CodeEntity, str]]:
        """提取类声明和内容

        Returns:
            类实体和类体的列表
        """
        classes = []
        lines = source_code.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            # 匹配类/接口/枚举声明
            class_match = re.search(
                r'((?:@[\w]+\s*)*)?'  # 注解
                r'((?:public|private|protected|static|final|abstract)\s+)*'  # 修饰符
                r'(class|interface|enum)\s+'  # 类型
                r'(\w+)',  # 类名
                line
            )

            if class_match:
                annotations = self._get_annotations_str(class_match.group(1) or "")
                modifiers = self._get_modifiers_list(class_match.group(2) or "")
                class_type = class_match.group(3)
                class_name = class_match.group(4)

                # 查找类的结束位置
                brace_count = 0
                start_line = i
                class_lines = []
                in_class = False

                for j in range(i, len(lines)):
                    class_lines.append(lines[j])
                    brace_count += lines[j].count('{')
                    brace_count -= lines[j].count('}')
                    if brace_count > 0:
                        in_class = True
                    elif in_class and brace_count == 0:
                        # 找到类结束
                        class_body = '\n'.join(class_lines)
                        qualified_name = f"{package}.{class_name}" if package else class_name

                        entity = CodeEntity(
                            name=class_name,
                            qualified_name=qualified_name,
                            type=class_type,
                            file_path=file_path,
                            start_line=start_line + 1,
                            end_line=j + 1,
                            modifiers=modifiers,
                            annotations=annotations
                        )

                        classes.append((entity, class_body))
                        i = j
                        break
            i += 1

        return classes

    def _parse_class(
        self,
        class_entity: CodeEntity,
        class_body: str,
        full_source: str,
        file_path: str,
        imports: List[str]
    ) -> None:
        """解析类内容"""
        # 添加类实体
        self.add_entity(class_entity)

        # 提取 extends
        extends_match = re.search(r'extends\s+([\w.]+)', class_body.split('{')[0])
        if extends_match:
            parent_name = extends_match.group(1)
            self.dependencies.append(Dependency(
                source_id=class_entity.id,
                target_name=parent_name,
                type="extend",
                file_path=file_path,
                line=class_entity.start_line
            ))

        # 提取 implements
        impl_match = re.search(r'implements\s+([\w.,\s]+)', class_body.split('{')[0])
        if impl_match:
            interfaces = impl_match.group(1).split(',')
            for iface in interfaces:
                iface = iface.strip()
                if iface:
                    self.dependencies.append(Dependency(
                        source_id=class_entity.id,
                        target_name=iface,
                        type="implement",
                        file_path=file_path,
                        line=class_entity.start_line
                    ))

        # 解析类成员
        self._parse_class_members(class_entity, class_body, file_path)

    def _parse_class_members(
        self,
        parent_entity: CodeEntity,
        class_body: str,
        file_path: str
    ) -> None:
        """解析类成员（方法、字段、构造函数）"""
        lines = class_body.split('\n')
        base_line = parent_entity.start_line

        # 跟踪是否在注释内
        in_multi_comment = False
        pending_annotations: List[str] = []  # 存储前面行的注解

        i = 0
        while i < len(lines):
            line = lines[i]
            original_line = line

            # 处理多行注释
            if '/*' in line:
                in_multi_comment = True
            if '*/' in line:
                in_multi_comment = False
                i += 1
                continue

            if in_multi_comment:
                i += 1
                continue

            stripped = line.strip()

            # 跳过空行和注释
            if not stripped or stripped.startswith('//'):
                i += 1
                continue

            # 跳过类声明行和结束大括号
            if stripped == '}' or 'class ' in stripped or 'interface ' in stripped or 'enum ' in stripped:
                pending_annotations = []  # 重置待处理的注解
                i += 1
                continue

            # 检查当前行是否有注解
            current_annotations = []
            annotation_match = re.match(r'^(@\w+(?:\([^)]*\))?)', stripped)
            if annotation_match:
                current_annotations = [annotation_match.group(1)]
                # 移除注解部分继续解析
                stripped = stripped[annotation_match.end():].strip()

            # 如果注解单独一行，保存它
            if not stripped and annotation_match:
                pending_annotations = current_annotations
                i += 1
                continue

            # 合并待处理的注解
            all_annotations = pending_annotations + current_annotations
            pending_annotations = []  # 重置

            # 解析方法
            method_match = re.match(
                r'((?:public|private|protected|static|final|abstract|synchronized|native)\s+)*'  # 修饰符
                r'([\w.<>]+\s+)?'  # 返回类型
                r'(\w+)\s*'  # 方法名
                r'\(([^)]*)\)',  # 参数
                stripped
            )

            if method_match and method_match.group(3) not in ['if', 'for', 'while', 'switch', 'catch', 'else', 'do']:
                modifiers = self._get_modifiers_list(method_match.group(1) or "")
                return_type = method_match.group(2) or "void"
                method_name = method_match.group(3)
                params = method_match.group(4)

                # 计算行号
                current_line = base_line + class_body[:class_body.find(original_line)].count('\n') + i + 1

                # 查找方法结束位置
                end_line = current_line
                brace_count = stripped.count('{') - stripped.count('}')
                for j in range(i + 1, len(lines)):
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    if brace_count <= 0:
                        end_line = base_line + class_body[:class_body.find(lines[j])].count('\n') + j + 1
                        break

                entity = CodeEntity(
                    name=method_name,
                    qualified_name=f"{parent_entity.qualified_name}.{method_name}",
                    type="method",
                    file_path=file_path,
                    start_line=current_line,
                    end_line=end_line,
                    modifiers=modifiers,
                    annotations=all_annotations,
                    signature=f"{method_name}({params})",
                    parent_id=parent_entity.id
                )
                self.add_entity(entity)
                i += 1
                continue

            # 解析构造函数
            constructor_match = re.match(
                r'((?:public|private|protected)\s+)*'  # 修饰符
                r'(\w+)\s*'  # 构造函数名
                r'\(([^)]*)\)',  # 参数
                stripped
            )

            if constructor_match and constructor_match.group(2)[0].isupper():
                modifiers = self._get_modifiers_list(constructor_match.group(1) or "")
                constructor_name = constructor_match.group(2)
                params = constructor_match.group(3)

                current_line = base_line + class_body[:class_body.find(original_line)].count('\n') + i + 1

                # 查找构造函数结束位置
                end_line = current_line
                brace_count = stripped.count('{') - stripped.count('}')
                for j in range(i + 1, len(lines)):
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    if brace_count <= 0:
                        end_line = base_line + class_body[:class_body.find(lines[j])].count('\n') + j + 1
                        break

                entity = CodeEntity(
                    name=constructor_name,
                    qualified_name=f"{parent_entity.qualified_name}.{constructor_name}",
                    type="constructor",
                    file_path=file_path,
                    start_line=current_line,
                    end_line=end_line,
                    modifiers=modifiers,
                    annotations=all_annotations,
                    signature=f"{constructor_name}({params})",
                    parent_id=parent_entity.id
                )
                self.add_entity(entity)
                i += 1
                continue

            # 解析字段
            field_match = re.match(
                r'((?:public|private|protected|static|final|volatile|transient)\s+)*'  # 修饰符
                r'([\w.<>[\]]+)\s+'  # 类型
                r'([\w,\s=]+)'  # 字段名
                r';',
                stripped
            )

            if field_match:
                modifiers = self._get_modifiers_list(field_match.group(1) or "")
                field_type = field_match.group(2).strip()
                field_names_str = field_match.group(3)

                # 处理多个字段
                field_names = [n.strip().split('=')[0].strip() for n in field_names_str.split(',')]

                current_line = base_line + class_body[:class_body.find(original_line)].count('\n') + i + 1

                for field_name in field_names:
                    if field_name and field_name[0].islower():
                        entity = CodeEntity(
                            name=field_name,
                            qualified_name=f"{parent_entity.qualified_name}.{field_name}",
                            type="field",
                            file_path=file_path,
                            start_line=current_line,
                            end_line=current_line,
                            modifiers=modifiers,
                            annotations=all_annotations,
                            signature=field_type,
                            parent_id=parent_entity.id
                        )
                        self.add_entity(entity)

            i += 1

    def _get_annotations_str(self, annotation_text: str) -> List[str]:
        """从文本中提取注解"""
        return self.ANNOTATION_PATTERN.findall(annotation_text)

    def _get_modifiers_list(self, modifier_text: str) -> List[str]:
        """从文本中提取修饰符"""
        return [m for m in self.MODIFIERS if m in modifier_text]
