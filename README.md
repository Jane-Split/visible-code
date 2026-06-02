# CodeViz - 企业级代码可视化平台

> 将代码逻辑、架构关系、数据流向以可视化方式呈现，支持多语言解析、实时变更检测和 SpringCloud 微服务可视化。

[English](#english) | [中文](#中文)

---

## 中文

### 🎯 项目简介

CodeViz 是一个面向企业级项目的代码可视化平台，能够将代码的逻辑结构、架构关系、数据流向以动态、交互式的方式呈现。支持从 Git 仓库或本地目录导入项目，自动解析代码结构并生成多种可视化视图。

### ✨ 核心功能

| 功能 | 描述 |
|------|------|
| 🏗️ **架构依赖图** | 交互式展示类、接口、模块之间的依赖与继承关系，支持缩放、拖拽、搜索过滤 |
| 🔀 **控制流图** | D3.js 驱动的代码逻辑流程可视化，支持播放/暂停动画 |
| 📊 **数据流图** | 数据血缘追踪，展示数据在系统中的流转路径 |
| 🌐 **微服务拓扑** | SpringCloud 微服务架构可视化，展示服务间调用关系、网关路由、FeignClient 依赖 |
| 🎬 **执行动画** | 代码执行步骤逐步动画，展示变量状态和调用栈变化 |
| 📡 **实时变更检测** | 基于 Watchdog 文件监听 + Git 轮询，代码变更实时反映到可视化视图 |
| 🔗 **双向联动** | 点击图节点跳转到对应代码，点击代码高亮对应节点 |
| 📤 **多格式导出** | 支持 PNG、SVG、JSON、PDF 格式导出 |

### 🛠️ 技术栈

**前端**
- React 18 + TypeScript 5
- React Flow — 架构图与微服务拓扑
- D3.js — 控制流图与数据流图
- Monaco Editor — 代码面板
- Ant Design 5 — UI 组件库
- Vite — 构建工具

**后端**
- Python 3.11+ / FastAPI
- SQLAlchemy + SQLite — 数据持久化
- Tree-sitter / 正则表达式 — 多语言 AST 解析
- Watchdog — 文件系统监听
- GitPython — Git 操作
- WebSocket — 实时通信

### 📁 目录结构

```
visible-code/
├── .gitignore
├── README.md
├── backend/                    # 后端服务
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── api/                # REST API 路由
│   │   │   ├── projects.py     # 项目管理
│   │   │   ├── graphs.py       # 图数据（依赖图、调用链）
│   │   │   ├── parser.py       # 解析调度
│   │   │   └── microservices.py # 微服务
│   │   ├── core/               # 核心模块
│   │   │   ├── config.py       # 配置
│   │   │   ├── database.py     # 数据库
│   │   │   ├── git.py          # Git 操作
│   │   │   ├── websocket.py    # WebSocket
│   │   │   └── cache.py        # 缓存
│   │   ├── models/             # ORM 数据模型
│   │   │   ├── project.py      # 项目
│   │   │   ├── entity.py       # 代码实体
│   │   │   ├── graph.py        # 依赖关系 / 调用链
│   │   │   └── microservice.py # 微服务模型
│   │   ├── parser/             # 代码解析引擎
│   │   │   ├── tree_sitter.py  # Tree-sitter 管理器
│   │   │   ├── scheduler.py    # 解析调度器
│   │   │   └── analyzers/      # 语言分析器
│   │   │       ├── base.py    # 分析器基类
│   │   │       ├── java.py    # Java 分析器
│   │   │       └── typescript.py # TypeScript 分析器
│   │   ├── microservice/       # 微服务分析
│   │   │   ├── analyzer.py     # SpringCloud 分析器
│   │   │   └── topology.py     # 服务拓扑构建
│   │   └── watcher/            # 实时变更检测
│   │       ├── file_watcher.py # 文件监听
│   │       ├── git_poller.py   # Git 轮询
│   │       └── event_processor.py # 事件处理
│   └── tests/                  # 单元测试
├── frontend/                   # 前端应用
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── App.tsx             # 路由定义
│       ├── main.tsx            # 入口
│       ├── services/
│       │   └── api.ts          # API 客户端
│       ├── utils/
│       │   ├── graphUtils.ts   # 图数据处理
│       │   └── exportUtils.ts  # 导出工具
│       ├── components/
│       │   ├── Layout.tsx      # 全局布局
│       │   ├── ArchitectureView/ # 架构图
│       │   ├── CodePanel/      # 代码面板
│       │   ├── FlowView/       # 控制流图
│       │   ├── DataFlowView/   # 数据流图
│       │   ├── ExecutionAnimation/ # 执行动画
│       │   ├── ExportToolbar/   # 导出工具栏
│       │   ├── MicroserviceView/ # 微服务拓扑
│       │   └── ProjectManager/ # 项目管理
│       └── pages/              # 页面
└── docs/                       # 文档
    └── code-visualizer-design.md
```

### 🚀 快速开始

**环境要求**
- Python 3.11+
- Node.js 18+
- Git

**1. 克隆项目**

```bash
git clone https://github.com/Jane-Split/visible-code.git
cd visible-code
```

**2. 启动后端**

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

后端服务运行在 `http://localhost:8000`，API 文档：`http://localhost:8000/docs`

**3. 启动前端**

```bash
cd frontend
npm install
npm run dev
```

前端服务运行在 `http://localhost:5173`，API 请求自动代理到后端。

### 📖 使用指南

1. **创建项目** — 在项目列表页点击「新建项目」，输入 Git 仓库地址或选择本地目录
2. **启动解析** — 项目创建后自动触发代码解析，也可手动触发
3. **查看可视化** — 解析完成后进入项目详情，切换不同视图：
   - **架构图** — 查看类/模块依赖关系
   - **控制流图** — 查看方法执行逻辑
   - **数据流图** — 追踪数据流向
   - **微服务拓扑** — 查看服务间调用关系
4. **双向联动** — 点击图节点查看对应代码，点击代码定位到图中节点
5. **导出** — 使用导出工具栏将可视化结果导出为 PNG/SVG/JSON/PDF

### 🔌 API 概览

| 模块 | 端点 | 说明 |
|------|------|------|
| 项目管理 | `POST /api/projects/` | 创建项目 |
| 项目管理 | `GET /api/projects/` | 项目列表 |
| 项目管理 | `POST /api/projects/{id}/sync` | 同步 Git 仓库 |
| 图数据 | `GET /api/projects/{id}/graphs/dependency` | 依赖图 |
| 图数据 | `GET /api/projects/{id}/graphs/call-chain` | 调用链 |
| 图数据 | `GET /api/projects/{id}/graphs/entity/{eid}` | 实体详情 |
| 解析 | `POST /api/projects/{id}/parser/start` | 启动解析 |
| 解析 | `GET /api/projects/{id}/parser/status` | 解析状态 |
| 微服务 | `GET /api/projects/{id}/microservices/topology` | 服务拓扑 |
| 微服务 | `POST /api/projects/{id}/microservices/analyze` | 微服务分析 |
| 实时通信 | `WS /ws/projects/{id}` | WebSocket 推送 |

完整 API 文档请访问 `http://localhost:8000/docs`（Swagger UI）。

### 🌐 支持的语言

| 语言 | 解析方式 | 支持程度 |
|------|----------|----------|
| Java | 正则表达式 + Tree-sitter | ✅ 完整支持（含 SpringCloud 注解） |
| TypeScript | 正则表达式 + Tree-sitter | ✅ 完整支持 |
| JavaScript | 正则表达式 | ✅ 基础支持 |
| Python | 正则表达式 | ✅ 基础支持 |
| Go | 正则表达式 | ✅ 基础支持 |

### 📜 License

MIT

---

## English

### 🎯 About

CodeViz is an enterprise-grade code visualization platform that presents code logic, architecture relationships, and data flows in a dynamic, interactive way. It supports importing projects from Git repositories or local directories, automatically parses code structures, and generates multiple visualization views.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🏗️ **Architecture Dependency Graph** | Interactive visualization of dependencies and inheritance between classes, interfaces, and modules with zoom, drag, and search |
| 🔀 **Control Flow Graph** | D3.js-powered code logic flow visualization with play/pause animation |
| 📊 **Data Flow Diagram** | Data lineage tracking showing how data flows through the system |
| 🌐 **Microservice Topology** | SpringCloud microservice architecture visualization showing inter-service calls, gateway routes, and FeignClient dependencies |
| 🎬 **Execution Animation** | Step-by-step code execution animation showing variable states and call stack changes |
| 📡 **Real-time Change Detection** | Watchdog file monitoring + Git polling for instant visualization updates on code changes |
| 🔗 **Bidirectional Linking** | Click graph nodes to jump to code; click code to highlight graph nodes |
| 📤 **Multi-format Export** | Export to PNG, SVG, JSON, and PDF formats |

### 🛠️ Tech Stack

**Frontend**
- React 18 + TypeScript 5
- React Flow — Architecture graphs & microservice topology
- D3.js — Control flow & data flow diagrams
- Monaco Editor — Code panel
- Ant Design 5 — UI component library
- Vite — Build tool

**Backend**
- Python 3.11+ / FastAPI
- SQLAlchemy + SQLite — Data persistence
- Tree-sitter / Regex — Multi-language AST parsing
- Watchdog — File system monitoring
- GitPython — Git operations
- WebSocket — Real-time communication

### 📁 Directory Structure

```
visible-code/
├── .gitignore
├── README.md
├── backend/                    # Backend service
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── api/                # REST API routes
│   │   │   ├── projects.py     # Project management
│   │   │   ├── graphs.py       # Graph data (dependency, call chain)
│   │   │   ├── parser.py       # Parse scheduling
│   │   │   └── microservices.py # Microservices
│   │   ├── core/               # Core modules
│   │   │   ├── config.py       # Configuration
│   │   │   ├── database.py     # Database
│   │   │   ├── git.py          # Git operations
│   │   │   ├── websocket.py    # WebSocket
│   │   │   └── cache.py        # Cache
│   │   ├── models/             # ORM data models
│   │   │   ├── project.py      # Project
│   │   │   ├── entity.py       # Code entity
│   │   │   ├── graph.py        # Dependencies / Call chains
│   │   │   └── microservice.py # Microservice models
│   │   ├── parser/             # Code parsing engine
│   │   │   ├── tree_sitter.py  # Tree-sitter manager
│   │   │   ├── scheduler.py    # Parse scheduler
│   │   │   └── analyzers/      # Language analyzers
│   │   │       ├── base.py     # Analyzer base class
│   │   │       ├── java.py     # Java analyzer
│   │   │       └── typescript.py # TypeScript analyzer
│   │   ├── microservice/       # Microservice analysis
│   │   │   ├── analyzer.py     # SpringCloud analyzer
│   │   │   └── topology.py     # Service topology builder
│   │   └── watcher/            # Real-time change detection
│   │       ├── file_watcher.py # File watcher
│   │       ├── git_poller.py   # Git poller
│   │       └── event_processor.py # Event processor
│   └── tests/                  # Unit tests
├── frontend/                   # Frontend application
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── App.tsx             # Route definitions
│       ├── main.tsx            # Entry point
│       ├── services/
│       │   └── api.ts          # API client
│       ├── utils/
│       │   ├── graphUtils.ts   # Graph data utilities
│       │   └── exportUtils.ts  # Export utilities
│       ├── components/
│       │   ├── Layout.tsx      # Global layout
│       │   ├── ArchitectureView/ # Architecture graph
│       │   ├── CodePanel/      # Code panel
│       │   ├── FlowView/       # Control flow graph
│       │   ├── DataFlowView/   # Data flow diagram
│       │   ├── ExecutionAnimation/ # Execution animation
│       │   ├── ExportToolbar/   # Export toolbar
│       │   ├── MicroserviceView/ # Microservice topology
│       │   └── ProjectManager/ # Project management
│       └── pages/              # Pages
└── docs/                       # Documentation
    └── code-visualizer-design.md
```

### 🚀 Quick Start

**Prerequisites**
- Python 3.11+
- Node.js 18+
- Git

**1. Clone the repository**

```bash
git clone https://github.com/Jane-Split/visible-code.git
cd visible-code
```

**2. Start the backend**

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

The backend runs at `http://localhost:8000`. API docs: `http://localhost:8000/docs`

**3. Start the frontend**

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` with API requests proxied to the backend.

### 📖 Usage Guide

1. **Create a project** — Click "New Project" on the project list page, enter a Git repository URL or select a local directory
2. **Start parsing** — Code parsing is triggered automatically after project creation, or can be triggered manually
3. **Explore visualizations** — Once parsing is complete, enter the project detail and switch between views:
   - **Architecture Graph** — View class/module dependencies
   - **Control Flow Graph** — View method execution logic
   - **Data Flow Diagram** — Track data flow paths
   - **Microservice Topology** — View inter-service call relationships
4. **Bidirectional linking** — Click graph nodes to view corresponding code; click code to locate graph nodes
5. **Export** — Use the export toolbar to save visualizations as PNG/SVG/JSON/PDF

### 🔌 API Overview

| Module | Endpoint | Description |
|--------|----------|-------------|
| Projects | `POST /api/projects/` | Create a project |
| Projects | `GET /api/projects/` | List projects |
| Projects | `POST /api/projects/{id}/sync` | Sync Git repository |
| Graphs | `GET /api/projects/{id}/graphs/dependency` | Dependency graph |
| Graphs | `GET /api/projects/{id}/graphs/call-chain` | Call chain |
| Graphs | `GET /api/projects/{id}/graphs/entity/{eid}` | Entity details |
| Parser | `POST /api/projects/{id}/parser/start` | Start parsing |
| Parser | `GET /api/projects/{id}/parser/status` | Parsing status |
| Microservices | `GET /api/projects/{id}/microservices/topology` | Service topology |
| Microservices | `POST /api/projects/{id}/microservices/analyze` | Analyze microservices |
| Real-time | `WS /ws/projects/{id}` | WebSocket push |

For the full API documentation, visit `http://localhost:8000/docs` (Swagger UI).

### 🌐 Supported Languages

| Language | Parsing Method | Support Level |
|----------|----------------|----------------|
| Java | Regex + Tree-sitter | ✅ Full (including SpringCloud annotations) |
| TypeScript | Regex + Tree-sitter | ✅ Full |
| JavaScript | Regex | ✅ Basic |
| Python | Regex | ✅ Basic |
| Go | Regex | ✅ Basic |

### 📜 License

MIT
