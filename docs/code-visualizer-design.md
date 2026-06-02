# CodeViz - 企业级代码可视化平台设计方案

**版本**: v1.0  
**日期**: 2026-06-02  
**作者**: AI Assistant  

---

## 1. 项目概述

### 1.1 项目背景

CodeViz 是一个面向企业级项目的代码可视化平台，旨在将复杂的代码逻辑、架构关系、数据流向以可视化、动态的方式呈现，帮助团队实现：

- **新人培训**：快速理解项目架构和核心流程
- **代码评审**：可视化展示代码变更的影响范围
- **架构文档**：自动生成和更新技术文档

### 1.2 核心目标

| 目标 | 说明 |
|------|------|
| 多语言支持 | 支持 Java、TypeScript/JavaScript、Python、Go 等主流语言 |
| 三种可视化 | 交互式架构图/依赖图、代码逻辑流程图、数据流图 |
| 动态交互 | 图与代码双向联动、逐层下钻、执行动画 |
| 代码来源 | 支持 Git 仓库拉取和本地目录导入 |
| 部署方式 | 小团队内部部署，零配置启动 |
| **微服务支持** | **SpringCloud 微服务架构可视化：服务拓扑、调用链路、网关路由、业务领域模型** |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              前端层 (Frontend)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │   架构图视图   │  │   流程图视图   │  │   数据流视图   │  │   代码面板    │ │
│  │ (React Flow) │  │   (D3.js)    │  │   (D3.js)    │  │(Monaco Editor)│ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│         └─────────────────┴─────────────────┴─────────────────┘         │
│                                    │                                    │
│                              REST API / WebSocket                       │
│                              (增量图数据推送)                             │
└────────────────────────────────────┼────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────┐
│                              后端层 (Backend)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │   项目管理    │  │   解析调度器   │  │   可视化API   │  │  WebSocket  │ │
│  │ (Project Mgr)│  │   (Parser)   │  │   (Graph API)│  │   (Events)  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│         └─────────────────┴─────────────────┴─────────────────┘         │
│                                    │                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      变更监听层 (Watch Layer)                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
│  │  │  文件系统监听  │  │  Git 轮询器   │  │  变更事件队列  │            │  │
│  │  │ (Watchdog)   │  │ (Polling)    │  │ (Debounce)   │            │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┼────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────┐
│                              存储层 (Storage)                            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        SQLite 数据库                              │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │  │
│  │  │ 项目元数据 │ │ AST 缓存  │ │ 依赖关系  │ │ 调用链    │ │ 数据流   │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        文件系统缓存                               │  │
│  │  ┌──────────┐ ┌──────────┐                                        │  │
│  │  │ 原始代码  │ │ Git 仓库  │                                        │  │
│  │  └──────────┘ └──────────┘                                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

| 层级 | 技术 | 版本 | 选择理由 |
|------|------|------|----------|
| 前端框架 | React | 18.x | 生态最丰富，可视化库集成成熟 |
| 前端语言 | TypeScript | 5.x | 类型安全，开发体验好 |
| 架构图引擎 | React Flow | 12.x | 交互式节点图的最佳选择 |
| 流程图引擎 | D3.js | 7.x | 灵活度最高，适合复杂流程图 |
| 代码编辑器 | Monaco Editor | 最新 | VS Code 同款，支持语法高亮 |
| UI 组件库 | Ant Design | 5.x | 企业级组件，风格统一 |
| 后端框架 | FastAPI | 0.110+ | 异步支持好，开发效率高 |
| 后端语言 | Python | 3.11+ | Tree-sitter 绑定成熟 |
| AST 解析 | Tree-sitter | 最新 | 增量解析，40+ 语言支持 |
| 数据库 | SQLite | 3.x | 零配置，嵌入式，适合小团队 |
| 缓存 | Redis (可选) | 7.x | 大项目性能优化 |
| 文件监听 | Watchdog | 3.x | Python 文件系统事件监听 |
| 实时通信 | WebSocket | 原生 | 增量数据推送 |

---

## 3. 核心模块设计

### 3.1 项目管理模块 (Project Manager)

#### 3.1.1 功能职责

- Git 仓库拉取与更新
- 本地目录导入
- 项目配置管理（语言类型、忽略规则等）
- 分支切换与历史版本对比

#### 3.1.2 Git 集成详细设计

```
┌─────────────────────────────────────────────────────────────┐
│                      Git 集成流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户输入 ──→ 验证仓库 ──→ 本地克隆 ──→ 分支选择 ──→ 代码解析   │
│     │           │           │           │           │       │
│     ▼           ▼           ▼           ▼           ▼       │
│  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐       │
│  │URL/ │    │git  │    │git  │    │git  │    │触发  │       │
│  │本地  │    │ls- │    │clone│    │checkout│   │解析  │       │
│  │路径  │    │remote│   │     │    │     │    │调度器│       │
│  └─────┘    └─────┘    └─────┘    └─────┘    └─────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Git 操作流程：**

1. **仓库验证**
   ```bash
   # 检查 URL 是否有效
   git ls-remote <repo-url>
   
   # 检查本地目录是否为 Git 仓库
   git -C <local-path> rev-parse --git-dir
   ```

2. **本地克隆策略**
   - 首次导入：完整克隆到 `~/.codeviz/repos/<project-id>/`
   - 支持 shallow clone：`--depth 1` 加速大仓库首次导入
   - 支持 sparse checkout：只拉取指定目录

3. **增量更新机制**
   ```bash
   # 获取最新变更
   git fetch origin
   
   # 获取变更文件列表
   git diff --name-only HEAD..origin/main
   
   # 只解析变更的文件
   git pull origin main
   ```

4. **分支管理**
   - 列出所有分支：`git branch -a`
   - 切换分支时触发重新解析（或增量解析）
   - 支持对比两个分支的差异视图

#### 3.1.3 数据模型

```typescript
// 项目元数据
interface Project {
  id: string;                    // UUID
  name: string;                  // 项目名称
  sourceType: 'git' | 'local';   // 来源类型
  sourceUrl: string;             // Git URL 或本地路径
  localPath: string;             // 本地克隆路径
  defaultBranch: string;         // 默认分支
  currentBranch: string;         // 当前分支
  languages: string[];           // 检测到的语言列表
  lastSyncedAt: Date;            // 最后同步时间
  lastCommitHash: string;        // 最后解析的 commit
  status: 'pending' | 'parsing' | 'ready' | 'error';
  config: ProjectConfig;
}

// 项目配置
interface ProjectConfig {
  ignorePatterns: string[];      // 忽略文件模式
  includePatterns: string[];     // 包含文件模式
  maxFileSize: number;           // 最大文件大小（字节）
  parseDepth: 'shallow' | 'deep'; // 解析深度
  autoSync: boolean;             // 是否启用自动同步
  syncInterval: number;          // Git 轮询间隔（秒）
}
```

---

### 3.2 解析调度器模块 (Parser Scheduler)

#### 3.2.1 功能职责

- 调度 Tree-sitter 解析代码
- 管理解析任务队列
- 增量更新处理
- AST → 结构化数据转换

#### 3.2.2 解析流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        解析调度流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  文件发现 ──→ 语言检测 ──→ AST 解析 ──→ 语义分析 ──→ 数据存储     │
│     │           │           │           │           │          │
│     ▼           ▼           ▼           ▼           ▼          │
│  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐          │
│  │遍历  │    │文件  │    │Tree-│    │提取  │    │写入  │          │
│  │目录  │    │扩展名│    │sitter│   │关系  │    │SQLite│          │
│  │结构  │    │映射  │    │解析  │    │节点  │    │     │          │
│  └─────┘    └─────┘    └─────┘    └─────┘    └─────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.2.3 多语言支持设计

| 语言 | Tree-sitter 语法 | 语义分析插件 |
|------|------------------|--------------|
| Java | tree-sitter-java | 类/方法/字段提取、Spring 注解识别 |
| TypeScript | tree-sitter-typescript | 接口/类型/模块提取、装饰器识别 |
| JavaScript | tree-sitter-javascript | ES6+ 特性提取、模块导入导出 |
| Python | tree-sitter-python | 类/函数/导入提取、装饰器识别 |
| Go | tree-sitter-go | 包/接口/结构体提取 |

#### 3.2.4 增量更新策略

```python
# 伪代码：增量更新逻辑
def incremental_parse(project_id, repo_path):
    # 1. 获取上次解析的 commit hash
    last_commit = get_last_commit(project_id)
    
    # 2. 获取当前 HEAD commit
    current_commit = git_get_head(repo_path)
    
    if last_commit == current_commit:
        return  # 无变更，跳过
    
    # 3. 获取变更文件列表
    changed_files = git_diff_files(repo_path, last_commit, current_commit)
    
    # 4. 分类处理
    for file in changed_files:
        if file.status == 'deleted':
            remove_from_db(project_id, file.path)
        elif file.status in ['added', 'modified']:
            parse_file(project_id, file.path)
    
    # 5. 更新项目元数据
    update_project_commit(project_id, current_commit)
```

#### 3.2.5 提取的数据类型

```typescript
// 代码实体
interface CodeEntity {
  id: string;
  projectId: string;
  filePath: string;
  type: 'module' | 'class' | 'interface' | 'function' | 'method' | 'field';
  name: string;
  qualifiedName: string;         // 全限定名
  startLine: number;
  endLine: number;
  startColumn: number;
  endColumn: number;
  modifiers: string[];           // public, private, static 等
  annotations: string[];         // 注解/装饰器
  signature?: string;            // 方法签名
  docstring?: string;            // 文档注释
}

// 依赖关系
interface Dependency {
  id: string;
  projectId: string;
  sourceId: string;              // 源实体 ID
  targetId: string;              // 目标实体 ID
  type: 'import' | 'extend' | 'implement' | 'call' | 'reference';
  filePath: string;
  line: number;
  column: number;
}

// 调用链
interface CallChain {
  id: string;
  projectId: string;
  callerId: string;              // 调用者方法 ID
  calleeId: string;              // 被调用方法 ID
  filePath: string;
  line: number;
  column: number;
}

// 变更事件（用于 WebSocket 推送）
interface ChangeEvent {
  projectId: string;
  type: 'entity_added' | 'entity_removed' | 'entity_modified' | 'dependency_changed';
  timestamp: Date;
  entity?: CodeEntity;
  entityId?: string;
  dependency?: Dependency;
  filePath?: string;
}
```

---

### 3.3 可视化 API 模块 (Graph API)

#### 3.3.1 功能职责

- 提供图数据查询接口
- 支持多种图类型：依赖图、调用图、控制流图、数据流图
- 支持过滤、搜索、分页

#### 3.3.2 API 设计

```typescript
// 依赖图查询
GET /api/projects/{projectId}/graphs/dependency
Query Params:
  - rootId: string              // 根节点 ID（可选，默认全部）
  - depth: number               // 展开深度（默认 2）
  - type: 'module' | 'class' | 'function'  // 聚合粒度
  - includeExternal: boolean    // 是否包含外部依赖

Response:
{
  nodes: [
    { id, name, type, metrics: { lineCount, complexity } }
  ],
  edges: [
    { source, target, type, weight }
  ]
}

// 调用链查询
GET /api/projects/{projectId}/graphs/call-chain
Query Params:
  - methodId: string            // 起始方法 ID
  - direction: 'up' | 'down' | 'both'  // 上游/下游/双向
  - maxDepth: number            // 最大深度

// 控制流图（函数级别）
GET /api/projects/{projectId}/graphs/control-flow
Query Params:
  - functionId: string          // 函数 ID

Response:
{
  nodes: [
    { id, type: 'entry' | 'exit' | 'statement' | 'branch', label, line }
  ],
  edges: [
    { source, target, label, condition }
  ]
}

// 数据流图
GET /api/projects/{projectId}/graphs/data-flow
Query Params:
  - variableId: string          // 变量 ID 或方法 ID
  - scope: 'function' | 'method' | 'class'
```

#### 3.3.3 WebSocket 实时推送设计

**连接管理：**
```typescript
// 客户端连接
const ws = new WebSocket(`ws://localhost:8000/ws/projects/${projectId}`);

// 消息类型
interface WsMessage {
  type: 'connected' | 'parsing_progress' | 'change_event' | 'error';
  payload: any;
}
```

**推送场景：**

| 场景 | 消息类型 | 内容 |
|------|----------|------|
| 连接成功 | `connected` | 当前项目状态、最后同步时间 |
| 解析进度 | `parsing_progress` | 进度百分比、当前处理文件 |
| **代码变更** | `change_event` | 变更类型 + 增量数据 |
| 错误 | `error` | 错误信息 |

**变更事件消息格式：**
```typescript
// 实体添加
{
  type: 'change_event',
  payload: {
    eventType: 'entity_added',
    entity: { id, name, type, filePath, ... },
    timestamp: '2026-06-02T10:30:00Z'
  }
}

// 实体删除
{
  type: 'change_event',
  payload: {
    eventType: 'entity_removed',
    entityId: 'uuid-xxx',
    timestamp: '2026-06-02T10:30:00Z'
  }
}

// 实体修改
{
  type: 'change_event',
  payload: {
    eventType: 'entity_modified',
    entity: { id, name, type, ... },
    changedFields: ['name', 'signature'],
    timestamp: '2026-06-02T10:30:00Z'
  }
}

// 依赖关系变更
{
  type: 'change_event',
  payload: {
    eventType: 'dependency_changed',
    dependency: { sourceId, targetId, type, ... },
    changeType: 'added' | 'removed',
    timestamp: '2026-06-02T10:30:00Z'
  }
}
```

---

### 3.4 实时变更感知模块 (Watch Layer)

#### 3.4.1 功能职责

- 监听本地文件系统变更（本地目录场景）
- 轮询 Git 远程仓库变更（Git 仓库场景）
- 变更事件去重与防抖处理
- 触发增量解析并推送变更通知

#### 3.4.2 整体流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                        实时变更感知流程                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  代码变更发生                                                        │
│       │                                                             │
│       ├─ 本地文件修改 ──→ Watchdog 监听 ──┐                         │
│       │                                    │                         │
│       └─ Git 远程推送 ──→ 轮询/Webhook ───┤                         │
│                                            ▼                        │
│                                     变更事件队列                      │
│                                     (去重 + 500ms 防抖)               │
│                                            │                        │
│                                            ▼                        │
│                                     增量解析（Tree-sitter）           │
│                                     只处理变更文件                    │
│                                            │                        │
│                                            ▼                        │
│                                     SQLite 数据库更新                 │
│                                            │                        │
│                                            ▼                        │
│                                     WebSocket 推送增量数据            │
│                                            │                        │
│                                            ▼                        │
│                                     前端局部刷新                      │
│                                     (新增/删除/更新节点和边)           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### 3.4.3 文件系统监听（本地目录场景）

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio

class CodeFileEventHandler(FileSystemEventHandler):
    def __init__(self, project_id: str, event_queue: asyncio.Queue):
        self.project_id = project_id
        self.event_queue = event_queue
        self._debounce_timers = {}  # 文件路径 -> timer
    
    def on_modified(self, event):
        if event.is_directory or not self._is_code_file(event.src_path):
            return
        self._debounce(event.src_path, 'modified')
    
    def on_created(self, event):
        if event.is_directory or not self._is_code_file(event.src_path):
            return
        self._debounce(event.src_path, 'created')
    
    def on_deleted(self, event):
        if event.is_directory or not self._is_code_file(event.src_path):
            return
        self._debounce(event.src_path, 'deleted')
    
    def _debounce(self, file_path: str, event_type: str):
        """防抖：500ms 内同一文件多次变更只触发一次"""
        if file_path in self._debounce_timers:
            self._debounce_timers[file_path].cancel()
        
        async def delayed_emit():
            await asyncio.sleep(0.5)  # 500ms 防抖
            await self.event_queue.put({
                'project_id': self.project_id,
                'file_path': file_path,
                'event_type': event_type,
                'timestamp': datetime.now()
            })
            del self._debounce_timers[file_path]
        
        self._debounce_timers[file_path] = asyncio.create_task(delayed_emit())
    
    def _is_code_file(self, path: str) -> bool:
        extensions = {'.java', '.ts', '.tsx', '.js', '.jsx', '.py', '.go'}
        return any(path.endswith(ext) for ext in extensions)

# 启动监听
def start_file_watcher(project_id: str, watch_path: str, event_queue: asyncio.Queue):
    handler = CodeFileEventHandler(project_id, event_queue)
    observer = Observer()
    observer.schedule(handler, watch_path, recursive=True)
    observer.start()
    return observer
```

#### 3.4.4 Git 远程变更检测（Git 仓库场景）

**方案对比：**

| 方案 | 实现方式 | 实时性 | 复杂度 | 推荐场景 |
|------|----------|--------|--------|----------|
| **定时轮询** | 后端每隔 N 秒 `git fetch` 检查 | 中等（30s-5min） | 低 | 大多数场景 |
| **Webhook** | Git 服务器推送事件到 CodeViz | 高（秒级） | 高（需公网） | 有公网 IP 的场景 |

**定时轮询实现：**

```python
import asyncio
import subprocess
from datetime import datetime

class GitPoller:
    def __init__(self, project_id: str, repo_path: str, interval: int = 30):
        self.project_id = project_id
        self.repo_path = repo_path
        self.interval = interval  # 轮询间隔（秒）
        self._running = False
    
    async def start(self):
        """启动轮询循环"""
        self._running = True
        while self._running:
            try:
                await self._check_remote_changes()
            except Exception as e:
                logger.error(f"Git poll error: {e}")
            await asyncio.sleep(self.interval)
    
    async def _check_remote_changes(self):
        """检查远程是否有新提交"""
        # 获取上次解析的 commit
        last_commit = await get_last_commit_hash(self.project_id)
        
        # fetch 远程最新状态
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=self.repo_path,
            capture_output=True
        )
        
        # 获取当前分支远程最新 commit
        result = subprocess.run(
            ["git", "rev-parse", "origin/HEAD"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        remote_commit = result.stdout.strip()
        
        if remote_commit != last_commit:
            # 获取变更文件列表
            diff_result = subprocess.run(
                ["git", "diff", "--name-only", f"{last_commit}..{remote_commit}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            changed_files = diff_result.stdout.strip().split('\n')
            
            # 触发增量解析
            await trigger_incremental_parse(
                self.project_id,
                changed_files,
                remote_commit
            )
    
    def stop(self):
        self._running = False
```

#### 3.4.5 变更事件队列处理

```python
class ChangeEventProcessor:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.processors = {}
    
    async def start(self):
        """启动事件处理循环"""
        while True:
            event = await self.queue.get()
            await self._process_event(event)
    
    async def _process_event(self, event: dict):
        """处理变更事件"""
        project_id = event['project_id']
        file_path = event['file_path']
        event_type = event['event_type']
        
        # 1. 执行增量解析
        if event_type == 'deleted':
            await remove_from_db(project_id, file_path)
        else:
            await parse_file(project_id, file_path)
        
        # 2. 获取变更影响范围
        changes = await get_changes_since_last_sync(project_id)
        
        # 3. 构建变更事件消息
        change_events = self._build_change_events(changes)
        
        # 4. WebSocket 推送给所有订阅的客户端
        await websocket_manager.broadcast(project_id, {
            'type': 'change_event',
            'payload': change_events
        })
    
    def _build_change_events(self, changes: list) -> list:
        """将数据库变更转换为前端可消费的变更事件"""
        events = []
        for change in changes:
            if change.type == 'entity_added':
                events.append({
                    'eventType': 'entity_added',
                    'entity': serialize_entity(change.entity)
                })
            elif change.type == 'entity_removed':
                events.append({
                    'eventType': 'entity_removed',
                    'entityId': change.entity_id
                })
            # ... 其他变更类型
        return events
```

#### 3.4.6 前端增量更新

```typescript
// WebSocket 客户端
class CodeVizWebSocket {
  private ws: WebSocket;
  private graphView: GraphView;
  private codePanel: CodePanel;
  
  constructor(projectId: string, graphView: GraphView, codePanel: CodePanel) {
    this.graphView = graphView;
    this.codePanel = codePanel;
    this.ws = new WebSocket(`ws://localhost:8000/ws/projects/${projectId}`);
    this.ws.onmessage = this.handleMessage.bind(this);
  }
  
  private handleMessage(event: MessageEvent) {
    const message: WsMessage = JSON.parse(event.data);
    
    switch (message.type) {
      case 'connected':
        console.log('WebSocket 连接成功', message.payload);
        break;
        
      case 'parsing_progress':
        this.showProgress(message.payload);
        break;
        
      case 'change_event':
        this.handleChangeEvent(message.payload);
        break;
        
      case 'error':
        console.error('WebSocket 错误:', message.payload);
        break;
    }
  }
  
  private handleChangeEvent(events: ChangeEvent[]) {
    for (const event of events) {
      switch (event.eventType) {
        case 'entity_added':
          // 添加新节点到图中
          this.graphView.addNode(this.toReactFlowNode(event.entity));
          break;
          
        case 'entity_removed':
          // 从图中移除节点
          this.graphView.removeNode(event.entityId);
          break;
          
        case 'entity_modified':
          // 更新图中节点
          this.graphView.updateNode(event.entity.id, this.toReactFlowNode(event.entity));
          break;
          
        case 'dependency_changed':
          if (event.changeType === 'added') {
            this.graphView.addEdge(this.toReactFlowEdge(event.dependency));
          } else {
            this.graphView.removeEdge(event.dependency.id);
          }
          break;
      }
    }
    
    // 如果当前打开的文件有变更，刷新代码面板
    const currentFile = this.codePanel.currentFile;
    const affectedFiles = events
      .filter(e => e.filePath)
      .map(e => e.filePath);
    
    if (currentFile && affectedFiles.includes(currentFile)) {
      this.codePanel.refresh();
    }
  }
}
```

---

### 3.5 前端视图模块

#### 3.5.1 架构图视图 (Architecture View)

**功能特性：**
- 交互式节点图，支持缩放、拖拽、框选
- 节点可展开/折叠，逐层下钻
- 节点颜色按模块/类型区分
- 边线粗细表示依赖强度
- 支持搜索高亮

**数据转换：**
```typescript
// 后端数据 → React Flow 节点
function toReactFlowNodes(entities: CodeEntity[]): Node[] {
  return entities.map(e => ({
    id: e.id,
    type: e.type === 'module' ? 'moduleNode' : 'classNode',
    position: calculateLayout(e),  // 自动布局算法
    data: {
      label: e.name,
      type: e.type,
      metrics: e.metrics,
      expandable: hasChildren(e)
    }
  }));
}
```

#### 3.5.2 流程图视图 (Flow View)

**功能特性：**
- 展示函数/方法的控制流图
- 条件分支用菱形表示
- 循环结构可视化
- 支持逐步执行动画
- 点击节点跳转到源代码

**D3.js 渲染：**
```typescript
// 控制流图渲染
function renderControlFlow(svg: SVGElement, data: ControlFlowData) {
  // 使用 Dagre 自动布局
  const g = new dagre.graphlib.Graph();
  
  // 添加节点
  data.nodes.forEach(node => {
    g.setNode(node.id, {
      label: node.label,
      width: 120,
      height: 40,
      shape: node.type === 'branch' ? 'diamond' : 'rect'
    });
  });
  
  // 添加边
  data.edges.forEach(edge => {
    g.setEdge(edge.source, edge.target, {
      label: edge.condition
    });
  });
  
  // 计算布局
  dagre.layout(g);
  
  // 渲染到 SVG
  // ...
}
```

#### 3.5.3 数据流视图 (Data Flow View)

**功能特性：**
- 展示数据从输入到输出的完整路径
- 变量赋值、传递、使用链路
- 跨函数的数据流追踪
- 支持正向追踪和反向溯源

#### 3.5.4 代码面板 (Code Panel)

**功能特性：**
- Monaco Editor 代码展示
- 语法高亮
- 点击图节点自动定位到代码位置
- 代码选中时高亮对应的图节点（双向联动）

**双向联动实现：**
```typescript
// 图节点点击 → 代码定位
function onNodeClick(node: Node) {
  const entity = node.data;
  codeEditor.revealLineInCenter(entity.startLine);
  codeEditor.setSelection({
    startLineNumber: entity.startLine,
    startColumn: entity.startColumn,
    endLineNumber: entity.endLine,
    endColumn: entity.endColumn
  });
}

// 代码选中 → 图节点高亮
function onCodeSelectionChange(selection: Selection) {
  const entity = findEntityAtPosition(selection);
  if (entity) {
    graphView.highlightNode(entity.id);
    graphView.centerOnNode(entity.id);
  }
}
```

---

### 3.6 SpringCloud 微服务可视化模块 (Microservice View)

#### 3.6.1 功能概述

针对 SpringCloud 微服务架构的深度支持，提供多维度可视化：

| 可视化维度 | 说明 | 数据来源 |
|-----------|------|----------|
| **服务拓扑图** | 展示服务间的调用关系，形成完整的服务网格 | 静态代码分析 + 运行时数据 |
| **API 网关路由** | 展示 Gateway/Zuul 路由配置，请求转发路径 | 静态代码分析 |
| **跨服务调用链** | 展示跨服务的业务流程调用链路 | 静态代码分析 + 运行时数据 |
| **业务领域模型** | 展示领域驱动设计中的聚合根、实体、值对象关系 | 静态代码分析 |
| **数据血缘关系** | 展示数据在服务间的流转路径 | 静态代码分析 |

#### 3.6.2 静态代码分析

**解析目标：**

```java
// @FeignClient 服务间调用
@FeignClient(name = "order-service", path = "/api/orders")
public interface OrderClient {
    @GetMapping("/{id}")
    Order getOrder(@PathVariable Long id);
}

// @RestController 服务提供者
@RestController
@RequestMapping("/api/users")
public class UserController {
    @Autowired
    private OrderClient orderClient;  // 依赖注入
    
    @GetMapping("/{id}/orders")
    public List<Order> getUserOrders(@PathVariable Long id) {
        return orderClient.getOrdersByUserId(id);  // 跨服务调用
    }
}

// Gateway 路由配置
@Configuration
public class GatewayConfig {
    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("user-service", r -> r.path("/api/users/**")
                .uri("lb://user-service"))
            .route("order-service", r -> r.path("/api/orders/**")
                .uri("lb://order-service"))
            .build();
    }
}

// application.yml 配置
spring:
  application:
    name: user-service
  cloud:
    gateway:
      routes:
        - id: order_route
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
```

**提取的元数据：**

```typescript
// 微服务定义
interface Microservice {
  id: string;
  projectId: string;
  name: string;                    // 服务名：user-service
  applicationClass: string;        // 主类名
  port: number;                    // 服务端口号
  contextPath: string;             // 上下文路径
  configFile: string;              // application.yml 路径
}

// FeignClient 调用
interface FeignClient {
  id: string;
  projectId: string;
  serviceId: string;               // 所属服务
  interfaceName: string;           // 接口全限定名
  targetService: string;           // 目标服务名：order-service
  path: string;                    // 基础路径：/api/orders
  methods: FeignMethod[];
}

interface FeignMethod {
  id: string;
  name: string;
  httpMethod: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  returnType: string;
  parameters: Parameter[];
  sourceLocation: Location;
}

// REST 端点
interface RestEndpoint {
  id: string;
  projectId: string;
  serviceId: string;
  controllerClass: string;
  methodName: string;
  httpMethod: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;                    // /api/users/{id}/orders
  fullPath: string;                // 拼接后的完整路径
  consumes: string[];              // Content-Type
  produces: string[];              // Accept
  parameters: Parameter[];
  returnType: string;
  sourceLocation: Location;
}

// Gateway 路由
interface GatewayRoute {
  id: string;
  projectId: string;
  routeId: string;                 // 路由标识
  sourcePath: string;              // /api/orders/**
  targetService: string;           // lb://order-service
  predicates: string[];            // Path、Method 等断言
  filters: string[];               // StripPrefix、Retry 等过滤器
  configSource: string;            // JavaConfig / YAML
  sourceLocation: Location;
}

// 服务间调用关系
interface ServiceCall {
  id: string;
  projectId: string;
  sourceService: string;           // 调用方服务名
  targetService: string;           // 被调用方服务名
  sourceEndpoint: string;          // 调用方端点 ID
  targetEndpoint: string;          // 被调用方端点 ID
  callType: 'feign' | 'restTemplate' | 'webClient';
  async: boolean;                  // 是否异步调用
  circuitBreaker: boolean;         // 是否有熔断
}

// 领域模型
interface DomainModel {
  id: string;
  projectId: string;
  serviceId: string;
  name: string;
  type: 'aggregate' | 'entity' | 'value_object';
  package: string;
  fields: DomainField[];
  methods: DomainMethod[];
  relationships: DomainRelationship[];
  annotations: string[];           // @Entity, @Table 等
  sourceLocation: Location;
}

interface DomainRelationship {
  targetModel: string;
  type: 'one_to_one' | 'one_to_many' | 'many_to_one' | 'many_to_many';
  mappedBy?: string;
  joinColumn?: string;
}
```

#### 3.6.3 运行时数据采集（可选增强）

```typescript
// 运行时服务实例
interface ServiceInstance {
  id: string;
  serviceId: string;
  instanceId: string;
  host: string;
  port: number;
  status: 'UP' | 'DOWN' | 'STARTING' | 'OUT_OF_SERVICE';
  metadata: Record<string, string>;
  lastHeartbeat: Date;
}

// 运行时调用链路（从 SkyWalking/Pinpoint 导入）
interface TraceSpan {
  id: string;
  traceId: string;
  spanId: string;
  parentSpanId: string;
  serviceName: string;
  operationName: string;           // 端点路径
  startTime: Date;
  duration: number;                // 毫秒
  status: 'success' | 'error';
  tags: Record<string, string>;
}
```

#### 3.6.4 可视化展示

**1. 服务拓扑图**

```typescript
// 服务拓扑图数据
interface ServiceTopology {
  nodes: ServiceNode[];
  edges: ServiceEdge[];
}

interface ServiceNode {
  id: string;
  name: string;
  type: 'gateway' | 'service' | 'external';
  status: 'healthy' | 'degraded' | 'unhealthy';
  instanceCount: number;
  endpoints: number;
}

interface ServiceEdge {
  source: string;
  target: string;
  type: 'sync' | 'async';
  callCount: number;               // 运行时统计
  avgLatency: number;              // 平均延迟
  errorRate: number;               // 错误率
}
```

展示效果：
- 服务节点按健康状态着色（绿/黄/红）
- 调用边线粗细表示调用频率
- 边线颜色表示延迟（绿<100ms，黄<500ms，红>500ms）
- 点击服务节点展开详情面板

**2. API 网关路由图**

```typescript
// 网关路由可视化
interface GatewayTopology {
  gateway: GatewayNode;
  routes: RouteMapping[];
}

interface RouteMapping {
  path: string;                    // /api/orders/**
  targetService: string;           // order-service
  predicates: string[];            // 匹配条件
  filters: string[];               // 过滤器链
  endpoints: RestEndpoint[];       // 目标服务的端点列表
}
```

展示效果：
- 中心为 Gateway 节点
- 放射状展示各服务路由
- 点击路由查看详细配置

**3. 跨服务调用链**

```typescript
// 业务流程调用链
interface BusinessFlow {
  id: string;
  name: string;                    // 下单流程
  entryService: string;            // 入口服务
  entryEndpoint: string;           // 入口端点
  steps: FlowStep[];
}

interface FlowStep {
  order: number;
  service: string;
  endpoint: string;
  operation: string;
  async: boolean;
  compensation?: string;           // 补偿操作（Saga 模式）
  nextSteps: number[];             // 下一步序号
}
```

展示效果：
- 时序图风格展示调用链
- 同步调用实线，异步调用虚线
- 支持展开查看每个步骤的详情

**4. 业务领域模型图**

```typescript
// DDD 领域模型图
interface DomainDiagram {
  aggregates: AggregateNode[];
  relationships: DomainEdge[];
}

interface AggregateNode {
  id: string;
  name: string;
  entities: EntityNode[];
  valueObjects: ValueObjectNode[];
  rootEntity: string;              // 聚合根
}

interface DomainEdge {
  source: string;
  target: string;
  type: 'contains' | 'references' | 'extends';
  cardinality: string;             // 1:1, 1:N, N:M
}
```

展示效果：
- 聚合边界用虚线框表示
- 实体用矩形，值对象用圆角矩形
- 关系连线标注 cardinality

#### 3.6.5 微服务 API 设计

```typescript
// 获取服务拓扑
GET /api/projects/{projectId}/microservices/topology
Response: ServiceTopology

// 获取服务详情
GET /api/projects/{projectId}/microservices/{serviceId}
Response: Microservice & { endpoints: RestEndpoint[], feignClients: FeignClient[] }

// 获取网关路由
GET /api/projects/{projectId}/microservices/gateway-routes
Response: GatewayRoute[]

// 获取跨服务调用链
GET /api/projects/{projectId}/microservices/call-chains
Query: { entryService?: string, entryEndpoint?: string }
Response: BusinessFlow[]

// 获取领域模型
GET /api/projects/{projectId}/microservices/domain-models
Query: { serviceId?: string }
Response: DomainDiagram

// 获取服务运行时状态（需集成 APM）
GET /api/projects/{projectId}/microservices/runtime-status
Response: { services: ServiceInstance[], metrics: ServiceMetrics }
```

---

## 4. 数据库设计

### 4.1 表结构

```sql
-- 项目表
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_type TEXT NOT NULL,  -- 'git' | 'local'
    source_url TEXT NOT NULL,
    local_path TEXT NOT NULL,
    default_branch TEXT,
    current_branch TEXT,
    languages TEXT,  -- JSON 数组
    last_synced_at TIMESTAMP,
    last_commit_hash TEXT,
    status TEXT,  -- 'pending' | 'parsing' | 'ready' | 'error'
    config TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 代码实体表
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'module' | 'class' | 'interface' | 'function' | 'method' | 'field'
    name TEXT NOT NULL,
    qualified_name TEXT NOT NULL,
    parent_id TEXT,
    start_line INTEGER,
    end_line INTEGER,
    start_column INTEGER,
    end_column INTEGER,
    modifiers TEXT,  -- JSON 数组
    annotations TEXT,  -- JSON 数组
    signature TEXT,
    docstring TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (parent_id) REFERENCES entities(id)
);

-- 依赖关系表
CREATE TABLE dependencies (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'import' | 'extend' | 'implement' | 'call' | 'reference'
    file_path TEXT,
    line INTEGER,
    column INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (source_id) REFERENCES entities(id),
    FOREIGN KEY (target_id) REFERENCES entities(id)
);

-- 调用链表
CREATE TABLE call_chains (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    caller_id TEXT NOT NULL,
    callee_id TEXT NOT NULL,
    file_path TEXT,
    line INTEGER,
    column INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (caller_id) REFERENCES entities(id),
    FOREIGN KEY (callee_id) REFERENCES entities(id)
);

-- 文件索引表（用于增量更新）
CREATE TABLE file_index (
    project_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,  -- MD5
    last_parsed_at TIMESTAMP,
    PRIMARY KEY (project_id, file_path)
);

-- 微服务表
CREATE TABLE microservices (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,           -- 服务名：user-service
    application_class TEXT,       -- 主类名
    port INTEGER,                 -- 服务端口号
    context_path TEXT,            -- 上下文路径
    config_file TEXT,             -- application.yml 路径
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- REST 端点表
CREATE TABLE rest_endpoints (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    service_id TEXT NOT NULL,
    controller_class TEXT NOT NULL,
    method_name TEXT NOT NULL,
    http_method TEXT NOT NULL,    -- GET | POST | PUT | DELETE
    path TEXT NOT NULL,           -- /api/users/{id}
    full_path TEXT NOT NULL,      -- 完整路径
    consumes TEXT,                -- JSON 数组
    produces TEXT,                -- JSON 数组
    parameters TEXT,              -- JSON
    return_type TEXT,
    file_path TEXT,
    start_line INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (service_id) REFERENCES microservices(id)
);

-- FeignClient 表
CREATE TABLE feign_clients (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    service_id TEXT NOT NULL,     -- 所属服务
    interface_name TEXT NOT NULL, -- 接口全限定名
    target_service TEXT NOT NULL, -- 目标服务名
    path TEXT,                    -- 基础路径
    file_path TEXT,
    start_line INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (service_id) REFERENCES microservices(id)
);

-- FeignClient 方法表
CREATE TABLE feign_methods (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    name TEXT NOT NULL,
    http_method TEXT NOT NULL,
    path TEXT,
    return_type TEXT,
    parameters TEXT,              -- JSON
    file_path TEXT,
    start_line INTEGER,
    FOREIGN KEY (client_id) REFERENCES feign_clients(id)
);

-- Gateway 路由表
CREATE TABLE gateway_routes (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    route_id TEXT NOT NULL,       -- 路由标识
    source_path TEXT NOT NULL,    -- /api/orders/**
    target_service TEXT NOT NULL, -- lb://order-service
    predicates TEXT,              -- JSON 数组
    filters TEXT,                 -- JSON 数组
    config_source TEXT,           -- JavaConfig | YAML
    file_path TEXT,
    start_line INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- 服务间调用关系表
CREATE TABLE service_calls (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    source_service TEXT NOT NULL, -- 调用方服务名
    target_service TEXT NOT NULL, -- 被调用方服务名
    source_endpoint TEXT,         -- 调用方端点 ID
    target_endpoint TEXT,         -- 被调用方端点 ID
    call_type TEXT,               -- feign | restTemplate | webClient
    async BOOLEAN DEFAULT FALSE,
    circuit_breaker BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- 领域模型表
CREATE TABLE domain_models (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    service_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,           -- aggregate | entity | value_object
    package TEXT,
    annotations TEXT,             -- JSON 数组
    file_path TEXT,
    start_line INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (service_id) REFERENCES microservices(id)
);

-- 领域关系表
CREATE TABLE domain_relationships (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,      -- 源模型 ID
    target_id TEXT NOT NULL,      -- 目标模型 ID
    type TEXT NOT NULL,           -- one_to_one | one_to_many | many_to_one | many_to_many
    mapped_by TEXT,
    join_column TEXT,
    FOREIGN KEY (source_id) REFERENCES domain_models(id),
    FOREIGN KEY (target_id) REFERENCES domain_models(id)
);

-- 索引
CREATE INDEX idx_entities_project ON entities(project_id);
CREATE INDEX idx_entities_file ON entities(file_path);
CREATE INDEX idx_entities_parent ON entities(parent_id);
CREATE INDEX idx_deps_source ON dependencies(source_id);
CREATE INDEX idx_deps_target ON dependencies(target_id);
CREATE INDEX idx_calls_caller ON call_chains(caller_id);
CREATE INDEX idx_calls_callee ON call_chains(callee_id);
CREATE INDEX idx_microservices_project ON microservices(project_id);
CREATE INDEX idx_endpoints_service ON rest_endpoints(service_id);
CREATE INDEX idx_feign_clients_service ON feign_clients(service_id);
CREATE INDEX idx_service_calls_source ON service_calls(source_service);
CREATE INDEX idx_service_calls_target ON service_calls(target_service);
CREATE INDEX idx_domain_models_service ON domain_models(service_id);
```

---

## 5. 部署方案

### 5.1 开发环境

```bash
# 1. 克隆项目
git clone <codeviz-repo>
cd codeviz

# 2. 安装后端依赖
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 安装前端依赖
cd ../frontend
npm install

# 4. 启动开发服务器
# 后端
cd ../backend
uvicorn main:app --reload --port 8000

# 前端（新终端）
cd frontend
npm run dev
```

### 5.2 生产环境部署

**Docker Compose 方案：**

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./repos:/app/repos
    environment:
      - DATABASE_URL=sqlite:///app/data/codeviz.db
      - REPOS_PATH=/app/repos
    
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

**单文件部署（推荐小团队）：**

```bash
# 构建单文件可执行版本
# 使用 PyInstaller + 静态前端嵌入
pyinstaller --onefile --add-data "frontend/dist:frontend" backend/main.py

# 运行
./codeviz
# 自动打开浏览器访问 http://localhost:8000
```

---

## 6. 安全与性能考虑

### 6.1 安全措施

| 风险 | 缓解措施 |
|------|----------|
| 恶意代码执行 | Tree-sitter 只解析 AST，不执行代码 |
| 敏感信息泄露 | 支持 `.gitignore` 类似的忽略规则 |
| 大文件 DoS | 设置最大文件大小限制（默认 1MB） |
| 路径遍历 | 所有文件操作限制在项目目录内 |

### 6.2 性能优化

| 场景 | 优化策略 |
|------|----------|
| 大项目首次解析 | 异步解析 + WebSocket 进度推送 |
| 超大图渲染 | 虚拟滚动 + 分层加载 |
| 频繁查询 | SQLite 索引 + 查询结果缓存 |
| 增量更新 | 文件哈希对比，只解析变更文件 |

---

## 7. 路线图

### Phase 1: MVP（4-6 周）
- [ ] 项目基础架构搭建
- [ ] Git 集成与本地导入
- [ ] Java/TypeScript 解析支持
- [ ] 基础架构图（模块依赖）
- [ ] 代码与图双向联动
- [ ] **实时变更感知（文件监听 + Git 轮询）**
- [ ] **WebSocket 增量推送与前端实时更新**

### Phase 2: 核心功能（4-6 周）
- [ ] Python/Go 解析支持
- [ ] 代码逻辑流程图
- [ ] 函数调用链追踪
- [ ] 增量更新优化
- [ ] 搜索与过滤
- [ ] **SpringCloud 微服务解析（@FeignClient、@RestController、Gateway）**
- [ ] **服务拓扑图与 API 网关路由可视化**
- [ ] **跨服务调用链追踪**
- [ ] **业务领域模型（DDD）可视化**

### Phase 3: 高级功能（4-6 周）
- [ ] 数据流图
- [ ] 执行动画
- [ ] 分支对比视图
- [ ] 导出功能（PNG/SVG/PDF）
- [ ] 性能优化（大项目支持）

---

## 8. 附录

### 8.1 目录结构

```
codeviz/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口
│   │   ├── api/
│   │   │   ├── projects.py      # 项目 API
│   │   │   ├── graphs.py        # 图数据 API
│   │   │   └── parser.py        # 解析 API
│   │   ├── core/
│   │   │   ├── config.py        # 配置管理
│   │   │   ├── database.py      # 数据库连接
│   │   │   ├── git.py           # Git 操作封装
│   │   │   └── websocket.py     # WebSocket 管理器
│   │   ├── watcher/             # 实时变更监听模块
│   │   │   ├── __init__.py
│   │   │   ├── file_watcher.py  # 文件系统监听
│   │   │   ├── git_poller.py    # Git 轮询器
│   │   │   └── event_processor.py # 变更事件处理器
│   │   ├── parser/
│   │   │   ├── __init__.py
│   │   │   ├── scheduler.py     # 解析调度器
│   │   │   ├── tree_sitter.py   # Tree-sitter 封装
│   │   │   └── analyzers/       # 各语言分析器
│   │   │       ├── java.py
│   │   │       ├── typescript.py
│   │   │       ├── python.py
│   │   │       └── go.py
│   │   ├── microservice/        # SpringCloud 微服务分析模块
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py      # 微服务分析器
│   │   │   ├── feign_parser.py  # FeignClient 解析
│   │   │   ├── gateway_parser.py # Gateway 路由解析
│   │   │   ├── domain_parser.py # DDD 领域模型解析
│   │   │   └── topology.py      # 服务拓扑构建
│   │   └── models/
│   │       ├── project.py
│   │       ├── entity.py
│   │       ├── graph.py
│   │       └── microservice.py  # 微服务相关模型
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ArchitectureView/   # 架构图视图
│   │   │   ├── FlowView/           # 流程图视图
│   │   │   ├── DataFlowView/       # 数据流视图
│   │   │   ├── CodePanel/          # 代码面板
│   │   │   ├── ProjectManager/     # 项目管理
│   │   │   └── MicroserviceView/   # 微服务可视化视图
│   │   │       ├── ServiceTopology/   # 服务拓扑图
│   │   │       ├── GatewayRoutes/     # 网关路由图
│   │   │       ├── CallChains/        # 跨服务调用链
│   │   │       └── DomainModels/      # 领域模型图
│   │   ├── services/
│   │   │   ├── api.ts              # API 客户端
│   │   │   └── websocket.ts        # WebSocket 客户端
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
├── docs/
│   └── code-visualizer-design.md   # 本设计文档
├── docker-compose.yml
└── README.md
```

### 8.2 相关技术文档

- [Tree-sitter 文档](https://tree-sitter.github.io/tree-sitter/)
- [React Flow 文档](https://reactflow.dev/)
- [D3.js 文档](https://d3js.org/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

---

**文档结束**
