# Implementation Plan: PromptX智能体集成

**Branch**: `001-promptx-integration` | **Date**: 2025-12-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-promptx-integration/spec.md`

## Summary

本功能在小智ESP32服务器的智控台中集成PromptX角色管理系统,使管理员能够创建配置PromptX智能体,用户能够直接与专业AI角色对话,无需手动激活。系统通过标准化的系统提示词模板引导LLM执行PromptX认知循环(action激活 → DMN扫描 → 多轮recall → 回答 → remember),保持动态记忆系统的更新能力。

技术方案:
- 后端新增API端点调用PromptX MCP的discover工具获取角色列表
- 前端roleConfig.vue组件扩展支持PromptX智能体类型
- 系统提示词模板存储为配置文件,支持变量替换(ROLE_ID、ROLE_NAME、ROLE_DESCRIPTION)
- 数据库扩展agent_config表存储PromptX特有字段
- LLM对话时通过系统提示词自动执行PromptX工具调用

## Technical Context

**Language/Version**:
- 后端: Python 3.10+ (基于现有xiaozhi-server环境)
- 前端: JavaScript/Vue.js 3.x (基于现有manager-web)

**Primary Dependencies**:
- 后端: FastAPI, SQLAlchemy (MySQL), httpx (用于调用PromptX MCP)
- 前端: Vue 3, Element Plus, Axios
- MCP集成: 现有mcp_manager.py模块

**Storage**:
- MySQL数据库 (扩展现有agent_config相关表)
- 配置文件: 系统提示词模板 (Markdown格式)

**Testing**:
- 后端: pytest (现有测试框架)
- 前端: Vitest/Jest (现有测试框架)
- 集成测试: 验证MCP工具调用链路

**Target Platform**:
- 服务端: Linux/macOS (Docker容器或本地Python环境)
- 客户端: 现代浏览器 (Chrome/Firefox/Safari)
- 依赖服务: PromptX MCP服务运行在localhost:5203

**Project Type**: Web应用 (前后端分离架构)

**Performance Goals**:
- 角色列表加载: <3秒
- 系统提示词生成: <100ms
- PromptX智能体对话响应: 相比普通智能体增加<2秒

**Constraints**:
- PromptX MCP服务必须在线运行
- LLM必须支持function calling (OpenAI/Claude等)
- 系统提示词模板不可被用户任意修改(保证认知循环正确性)

**Scale/Scope**:
- 支持50+个PromptX角色
- 预计10-50个PromptX智能体配置
- 与现有智能体系统共享用户和对话管理

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### 项目架构原则验证

由于本项目没有明确的constitution文件,基于现有代码库结构进行以下验证:

**✅ 模块化原则**:
- 功能在现有模块边界内扩展(后端mcp集成、前端智能体配置)
- 不引入新的微服务或独立模块
- 复用现有MCP管理器和智能体配置系统

**✅ 最小侵入性**:
- 前端只修改roleConfig.vue组件,不影响其他页面
- 后端新增API端点,不修改现有对话流程
- 数据库通过扩展字段集成,不改变现有表结构

**✅ 依赖管理**:
- 使用现有MCP集成机制(mcp_manager.py)
- 不引入新的外部依赖库
- PromptX MCP服务作为可选依赖(降级处理)

**✅ 测试策略**:
- 单元测试: API端点、模板生成逻辑
- 集成测试: MCP工具调用、数据库操作
- UI测试: 智能体创建流程、角色列表加载

**无违规项** - 本功能符合现有架构模式,无需特殊批准。

## Project Structure

### Documentation (this feature)

```text
specs/001-promptx-integration/
├── plan.md              # 本文件 (实施计划)
├── spec.md              # 功能规格说明
├── research.md          # Phase 0输出: 技术研究
├── data-model.md        # Phase 1输出: 数据模型
├── quickstart.md        # Phase 1输出: 快速开始指南
├── contracts/           # Phase 1输出: API合约
│   └── promptx-agent-api.yaml
├── checklists/          # 质量检查清单
│   └── requirements.md
└── tasks.md             # Phase 2输出: 任务分解 (由/speckit.tasks生成)
```

### Source Code (repository root)

本项目为Web应用,采用前后端分离架构:

```text
main/
├── xiaozhi-server/                    # 后端服务
│   ├── core/
│   │   ├── providers/
│   │   │   └── tools/
│   │   │       └── server_mcp/
│   │   │           ├── mcp_manager.py           # [修改] 扩展MCP管理器
│   │   │           └── promptx_service.py       # [新增] PromptX服务封装
│   │   └── config/
│   │       └── templates/
│   │           └── promptx_agent_prompt.md      # [新增] 系统提示词模板
│   ├── plugins_func/
│   │   └── functions/
│   │       └── change_role.py                   # [参考] 角色切换示例
│   ├── api/
│   │   └── routes/
│   │       └── promptx_agent.py                 # [新增] PromptX智能体API路由
│   ├── models/
│   │   └── agent_config.py                      # [修改] 扩展智能体配置模型
│   ├── data/
│   │   └── mcp_server_settings.json             # [已配置] PromptX MCP连接
│   └── tests/
│       ├── unit/
│       │   ├── test_promptx_service.py          # [新增] PromptX服务测试
│       │   └── test_promptx_agent_api.py        # [新增] API测试
│       └── integration/
│           └── test_promptx_mcp_integration.py  # [新增] MCP集成测试
│
└── manager-web/                       # 前端智控台
    ├── src/
    │   ├── views/
    │   │   └── roleConfig.vue                   # [修改] 智能体配置页面
    │   ├── components/
    │   │   └── PromptXRoleSelector.vue          # [新增] PromptX角色选择器
    │   ├── api/
    │   │   └── promptx.js                       # [新增] PromptX API客户端
    │   └── store/
    │       └── modules/
    │           └── promptxAgent.js              # [新增] Vuex状态管理
    └── tests/
        └── unit/
            └── components/
                └── PromptXRoleSelector.spec.js  # [新增] 组件测试
```

**Structure Decision**: 采用现有的前后端分离架构,后端在xiaozhi-server目录下扩展MCP集成和API,前端在manager-web目录下扩展智能体配置UI。所有修改都在现有模块边界内,不创建新的顶层目录或服务。

## Complexity Tracking

无需填写 - Constitution Check未检测到违规项。

## Phase 0: Research & Technical Decisions

### 研究任务列表

基于Technical Context中的技术选型,需要研究以下领域:

1. **PromptX MCP工具调用模式**
   - 研究discover工具的返回格式和角色数据结构
   - 确认action、recall、remember工具的调用参数
   - 了解MCP错误处理和降级策略

2. **系统提示词模板设计**
   - 研究最佳的Markdown模板格式
   - 确定变量替换的安全实现方式
   - 设计模板版本管理机制

3. **数据库模式扩展**
   - 分析现有agent_config表结构
   - 设计PromptX智能体字段扩展方案
   - 确保向后兼容性

4. **前端Vue组件集成**
   - 研究roleConfig.vue现有表单结构
   - 设计PromptX智能体类型的UI差异化
   - Element Plus组件选择和布局

5. **LLM工具调用验证**
   - 确认当前LLM配置支持function calling
   - 测试系统提示词对工具调用的引导效果
   - 设计工具调用日志格式

### 输出文件

详细研究结果将在 `research.md` 中记录。

## Phase 1: Design & Contracts

### 数据模型设计

输出文件: `data-model.md`

关键实体:
- PromptXAgent (扩展自现有Agent配置)
- PromptXRole (从MCP discover获取的角色信息)
- SystemPromptTemplate (模板和变量映射)

### API合约

输出文件: `contracts/promptx-agent-api.yaml`

关键端点:
- `GET /api/promptx/roles` - 获取PromptX角色列表
- `POST /api/agents/promptx` - 创建PromptX智能体
- `GET /api/agents/promptx/{id}` - 查询PromptX智能体详情
- `PUT /api/agents/promptx/{id}` - 更新PromptX智能体配置
- `POST /api/promptx/roles/refresh` - 刷新角色列表缓存

### 快速开始指南

输出文件: `quickstart.md`

涵盖:
- 开发环境设置
- PromptX MCP服务配置验证
- 本地运行和调试
- 测试数据准备

## Phase 2: Task Breakdown

**注意**: Phase 2的任务分解由 `/speckit.tasks` 命令生成,不在本plan.md中。

任务分解将包括:
- 后端API实现任务
- 前端UI组件实现任务
- 数据库迁移任务
- 测试编写任务
- 文档完善任务

每个任务将包含:
- 任务描述和验收标准
- 依赖关系
- 预估工作量
- 测试要求

---

**下一步**: 执行 `/speckit.tasks` 生成详细的任务分解和依赖关系。
