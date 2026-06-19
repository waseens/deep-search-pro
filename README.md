<p align="center">
  <h1 align="center">🤖 Deep Search Pro</h1>
  <p align="center"><b>一个轻量的多智能体协作系统 —— Agent 开发入门实战项目</b></p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.129.2-green.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/LangChain-1.2.10-orange.svg" alt="LangChain">
    <img src="https://img.shields.io/badge/deepagents-0.4.3-purple.svg" alt="deepagents">
    <img src="https://img.shields.io/badge/适合-学习练手-brightgreen.svg" alt="learning">
  </p>
</p>

---

## 🎯 这个项目是什么

这是一个 **不到 1000 行代码** 的 AI Agent 学习项目。它用最精简的方式展示了如何基于 LangChain 生态构建一个**多智能体协作系统**——一个"主智能体"像团队负责人一样调度三个"子智能体"（网络搜索、数据库查询、知识库检索）来协同完成复杂任务。

**如果你是以下人群，这个项目就是为你准备的 👇**

- 正在学习 LangChain / LangGraph，想找一个**完整的、能跑起来的**实战项目
- 对 "多智能体编排" 感兴趣，但不想一上来就看复杂的 AutoGPT / CrewAI 源码
- 想理解 **FastAPI + WebSocket + Agent** 怎么组合成一个真实可用的系统
- 面试前需要一个 AI Agent 项目来充实简历，并且能讲清楚每个设计决策

---

## 🧠 你能从这个项目中学到什么

| 知识点 | 具体体现在项目哪里 |
|--------|------------------|
| **Orchestrator 多智能体模式** | `agent/main_agent.py` — 主智能体如何调度 3 个子智能体 |
| **Prompt Engineering 实战** | `prompt/prompts.yml` — 如何用 system_prompt 约束 Agent 行为 |
| **LangChain @tool 自定义工具** | `tools/` 目录 — 6 个工具函数的完整写法 |
| **FastAPI 异步 + 后台任务** | `api/server.py` — `asyncio.create_task` 非阻塞执行 |
| **WebSocket 实时推送** | `api/monitor.py` — 工具调用进度实时推送到前端 |
| **ContextVar 协程级数据隔离** | `api/context.py` — 多用户并发时不串台 |
| **Agent 文件操作安全** | `utils/path_utils.py` — 12 种路径场景的防护 |
| **RAG 知识库对接** | `tools/ragflow_tools.py` — RAGFlow SDK 实战 |
| **数据库自然语言查询** | `tools/db_tools.py` — Agent 自动写 SQL 并执行 |

---

## 🏗️ 架构一览

整个项目只有 6 个核心模块，非常适合逐模块阅读学习：

```
用户请求 (POST /api/task)
    │
    ▼
api/server.py          ← 入门的第一个文件：FastAPI 的路由和 WebSocket
    │
    ▼
agent/main_agent.py    ← 核心：主智能体如何创建、如何异步流式执行
    │
    ├──→ 子智能体 1: 网络搜索     (tools/tavily_tool.py)
    ├──→ 子智能体 2: 数据库查询   (tools/db_tools.py)
    ├──→ 子智能体 3: RAGFlow知识库 (tools/ragflow_tools.py)
    │
    └──→ 主智能体自己调: 生成Markdown → 转PDF
    │
    ▼ (每个步骤都通过 WebSocket 实时推送)
api/monitor.py         ← 埋点监控 + 事件循环归属判断
    │
    ▼
前端收到实时进度："正在搜索网络..." → "正在查数据库..." → "正在生成文档..."
```

### 数据流说明

1. 用户通过 `POST /api/task` 发一个自然语言请求
2. 主智能体分析需求，决定调用哪些子智能体
3. 子智能体各司其职，去搜网络 / 查数据库 / 翻知识库
4. 主智能体拿到所有信息后，汇总成一份 Markdown 报告（或转 PDF）
5. 整个过程通过 WebSocket 实时推到前端，前端能看到每一步进度

---

## 🚀 5 分钟跑起来

### 环境要求

- Python 3.10+
- 一个 OpenAI 兼容的 LLM API Key（阿里云百炼 / DeepSeek / OpenAI 都可以）
- Tavily API Key（[免费额度注册](https://tavily.com)）

> 📌 数据库和 RAGFlow 是**可选的**，不配也能跑 —— 主智能体会自动跳过没有的服务。

### 第一步：克隆 + 装依赖

```bash
git clone https://github.com/你的用户名/deep-search-pro.git
cd deep-search-pro
pip install -r requirements.txt
```

### 第二步：配环境变量

```bash
cp .env.example .env
```

编辑 `.env`，最少只需要填 3 个：

```env
# 必填：LLM 服务（以阿里云百炼为例）
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_QWEN_MAX=qwen-max

# 必填：网络搜索
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx

# 以下可选，不填就只影响对应功能
# RAGFLOW_API_URL=...
# MYSQL_USER=...
```

### 第三步：启动

```bash
python api/server.py
```

访问 `http://localhost:8000/docs` 能看到 Swagger 文档，直接在页面上试。

### 第四步：试一试

```bash
curl -X POST http://localhost:8000/api/task \
  -H "Content-Type: application/json" \
  -d '{"query": "搜索一下最近AI Agent领域的最新进展"}'
```

同时在浏览器打开 WebSocket `ws://localhost:8000/ws/{返回的thread_id}`，就能看到实时推送的进度消息。

---

## 📖 推荐阅读顺序

如果你是第一次接触 AI Agent 项目，建议按这个顺序读代码：

| 顺序 | 文件 | 重点看什么 |
|------|------|-----------|
| 1️⃣ | `agent/llm.py` | 只有 10 行，看 LLM 怎么初始化的 |
| 2️⃣ | `prompt/prompts.yml` | 看系统提示词怎么写，怎么约束 Agent 行为 |
| 3️⃣ | `agent/subagents/network_search_agent.py` | 最简单的子智能体，理解"子智能体 = 字典配置" |
| 4️⃣ | `tools/tavily_tool.py` | 一个完整的 @tool 怎么写，埋点怎么做 |
| 5️⃣ | `agent/main_agent.py` | **核心**：主智能体怎么创建、怎么 orchestrate、怎么流式执行 |
| 6️⃣ | `api/server.py` | FastAPI 怎么和 Agent 结合，异步任务怎么触发 |
| 7️⃣ | `api/monitor.py` | WebSocket 实时推送，事件循环归属判断 |
| 8️⃣ | `api/context.py` | ContextVar 为什么比全局变量好 |
| 9️⃣ | `utils/path_utils.py` | Agent 文件安全——边界场景大全 |

---

## 📁 项目文件速查

```
deep_search_pro/
│
├── agent/                          # 🤖 智能体层（核心）
│   ├── llm.py                      # 模型初始化，10 行
│   ├── prompts.py                  # YAML 提示词加载
│   ├── main_agent.py               # ★ 主智能体 + 异步执行引擎
│   └── subagents/                  # 子智能体（每个就是一个字典）
│       ├── network_search_agent.py
│       ├── database_query_agent.py
│       └── knowledge_base_agent.py
│
├── api/                            # 🌐 Web 接口层
│   ├── server.py                   # FastAPI 入口
│   ├── context.py                  # ContextVar 协程隔离（带详细注释）
│   └── monitor.py                  # 监控 + WebSocket 连接池
│
├── tools/                          # 🔧 工具函数（6 个 @tool）
│   ├── tavily_tool.py              # 网络搜索
│   ├── db_tools.py                 # 数据库查询 3 件套
│   ├── ragflow_tools.py            # RAGFlow 知识库检索
│   ├── markdown_tools.py           # 生成 Markdown
│   ├── pdf_tools.py                # Markdown → PDF
│   └── upload_file_read_tool.py    # 读取上传文件
│
├── utils/                          # 🛠 工具层
│   ├── path_utils.py               # 路径安全解析（12 种场景）
│   └── word_converter.py           # Word COM 引擎
│
├── rawflow/                        # 📚 RAGFlow SDK 独立示例
├── prompt/prompts.yml              # 提示词配置
├── requirements.txt                # 依赖清单（版本锁定）
└── .env.example                    # 环境变量模板
```

---

## 🧪 练手建议：你可以这样改造

项目的设计刻意保持简洁，给你留了很多动手空间。以下是一些建议的改造方向，难度递进：

### 入门级（加深理解）

- [ ] **换个模型**：把通义千问换成 DeepSeek 或 GPT，改 `.env` 一行就行
- [ ] **加一个子智能体**：比如"天气查询助手"或"代码执行助手"，体验一下加子智能体要多改几行代码
- [ ] **改 system_prompt**：把"空调公司"改成你自己的业务场景，看看 Agent 行为怎么变化

### 进阶级（工程能力）

- [ ] **把 InMemorySaver 换成 SqliteSaver**：让对话历史持久化，重启不丢失
- [ ] **加一个简单的 Web 前端**：用聊天界面替代 curl，WebSocket 显示实时进度条
- [ ] **给子智能体加"反思"机制**：让子智能体执行完后再自我检查一遍，提高准确性
- [ ] **加 JWT 认证**：给 `/api/task` 加上登录校验

### 挑战级（深入学习）

- [ ] **把 Word COM 换成 WeasyPrint**：摆脱 Windows 依赖，让 PDF 转换在 Linux 上跑
- [ ] **用 LangGraph 的 checkpointer 实现"人工审批节点"**：敏感操作需要用户确认才执行
- [ ] **给子智能体之间加"通信"**：让数据库子智能体和网络搜索子智能体能互相交换信息
- [ ] **Docker 化**：写 Dockerfile + docker-compose，一键启动所有依赖

---

## 🔧 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| Agent 框架 | **deepagents** (LangChain 官方) | 多智能体编排，本项目核心依赖 |
| LLM 接入 | LangChain + OpenAI 兼容协议 | 一套代码适配多种模型 |
| Web 框架 | FastAPI + Uvicorn | 异步 HTTP + 原生 WebSocket |
| 搜索引擎 | Tavily API | AI 专用搜索，提供免费额度 |
| 知识库 | RAGFlow | 开源的 RAG 引擎，可以本地部署 |
| 数据库 | MySQL | 关系型数据库，Agent 自动写 SQL |
| 文档生成 | markdown + pywin32 | MD 生成 + Word COM 转 PDF |

---

## ❓ FAQ

### Q: 为什么选 deepagents 而不是自己写编排逻辑？

**A:** 自己写编排要处理状态管理、tool_call 路由、流式输出、错误恢复等一堆事。`deepagents` 把这些都封装好了，你只需要定义子智能体的 name / description / tools，框架帮你调度。对学习来说，先理解"用框架能做什么"，之后再看源码理解"框架怎么做的"。

### Q: 没有 RAGFlow 和 MySQL，项目还能跑吗?

**A:** 能。主智能体会根据 system_prompt 判断只有"网络搜索"可用，自动跳过另外两个子智能体。只配 LLM + Tavily 就能体验完整链路。当然功能会受限——这就是刻意设计的"优雅降级"。

### Q: 为什么用 ContextVar 而不是全局变量？

**A:** FastAPI 下多个请求跑在同一个线程的不同协程里。如果用全局变量，用户 A 的数据会被用户 B 覆盖（串台）。ContextVar 是 Python 为 asyncio 设计的协程级变量，每个请求链路互不干扰。`api/context.py` 里有详细注释解释这个问题。

### Q: 项目为什么不到 1000 行？

**A:** 故意的。这是给学习用的项目，不是给生产用的。每个模块只做一件事，代码量少才容易看懂。如果你能把这 1000 行都读明白，多智能体 Agent 的核心概念就掌握了。

---

## 📄 License

MIT License —— 随便用，改，分叉。如果你基于这个项目做了有趣的东西，欢迎提 PR 或者告诉我 😄
