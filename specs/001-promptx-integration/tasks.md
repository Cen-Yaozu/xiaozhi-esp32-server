# Tasks: PromptX智能体集成

**Input**: Design documents from `/specs/001-promptx-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: 本功能未明确要求TDD方法,因此测试任务为可选。建议在实现完成后编写集成测试验证功能。

**Organization**: 任务按用户故事组织,使每个故事可以独立实现和测试。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行(不同文件,无依赖)
- **[Story]**: 所属用户故事(US1, US2, US3, US4)
- 包含精确的文件路径

## Path Conventions

本项目为Web应用(前后端分离):
- **后端**: `main/xiaozhi-server/`
- **前端**: `main/manager-web/`

---

## Phase 1: Setup (共享基础设施)

**Purpose**: 项目初始化和基础结构准备

- [X] T001 复制系统提示词模板到后端配置目录 main/xiaozhi-server/config/templates/promptx_agent_system_prompt_template.md
- [X] T002 验证PromptX MCP服务配置在 main/xiaozhi-server/mcp_server_settings.json 中正确
- [X] T003 [P] 创建数据库迁移脚本 main/xiaozhi-server/mysql/migrations/v1.0.0_add_promptx_support.sql
- [X] T004 [P] 创建数据库回滚脚本 main/xiaozhi-server/mysql/migrations/rollback_v1.0.0_remove_promptx_support.sql
- [ ] T078 [P] 创建快速开始指南 specs/001-promptx-integration/quickstart.md

---

## Phase 2: Foundational (阻塞性先决条件)

**Purpose**: 所有用户故事必须依赖的核心基础设施

**⚠️ CRITICAL**: 在此阶段完成前,不能开始任何用户故事的实现

- [X] T005 执行数据库迁移,在 ai_agent 和 ai_agent_template 表中添加 agent_type, promptx_role_id, promptx_role_source 字段
- [X] T006 [P] 扩展后端实体类 main/manager-api/src/main/java/xiaozhi/modules/agent/entity/ (AgentEntity, AgentTemplateEntity) 添加PromptX字段
- [X] T007 [P] 创建PromptX角色DTO main/manager-api/src/main/java/xiaozhi/modules/agent/dto/ (PromptXRoleDTO, GeneratePromptRequest, 扩展AgentCreateDTO)
- [X] T008 创建PromptX服务封装 main/xiaozhi-server/core/providers/tools/server_mcp/promptx_service.py (调用MCP工具的核心逻辑)
- [X] T009 实现系统提示词模板生成逻辑 main/xiaozhi-server/core/promptx_template_service.py (读取模板,替换变量)

**Checkpoint**: 基础设施就绪 - 用户故事实现现在可以并行开始

---

## Phase 3: User Story 1 - 创建PromptX智能体 (Priority: P1) 🎯 MVP

**Goal**: 管理员能够在智控台创建PromptX智能体,选择角色并自动生成系统提示词

**Independent Test**:
1. 管理员访问智控台
2. 选择"PromptX智能体"类型
3. 从角色列表选择角色(如"产品经理")
4. 填写智能体名称并保存
5. 验证配置成功保存到数据库,系统提示词正确生成

### 后端实现 - User Story 1

#### Python层(xiaozhi-server) - 内部HTTP API
- [X] T010 [P] [US1] 实现GET /api/promptx/roles端点在 main/xiaozhi-server/core/api/promptx_handler.py
- [X] T011 [P] [US1] 实现POST /api/promptx/generate-prompt端点在 main/xiaozhi-server/core/api/promptx_handler.py
- [X] T013 [US1] 在promptx_service.py中实现get_promptx_roles方法(调用MCP discover工具)
- [X] T014 [US1] 在promptx_template_service.py中实现generate_system_prompt方法(变量替换)

#### Java层(manager-api) - 公开REST API
- [x] T012 [US1] 创建PromptXService.java (调用Python HTTP API)
- [x] T076 [US1] 创建PromptXController.java (暴露REST API给前端)
- [x] T077 [US1] 实现POST /api/agents/promptx端点(创建PromptX智能体)
- [ ] T015 [US1] 添加数据验证逻辑,确保PromptX智能体字段完整性在 main/xiaozhi-server/validators/agent_validator.py
- [ ] T016 [US1] 实现MCP服务不可用时的错误处理和降级逻辑
- [ ] T017 [US1] 添加MCP工具调用日志记录到 main/xiaozhi-server/logs/mcp_calls.log

### 前端实现 - User Story 1

- [X] T018 [P] [US1] 创建PromptX API客户端 main/manager-web/src/apis/module/promptx.js (getPromptXRoles, generateSystemPrompt)
- [x] T019 [P] [US1] 创建PromptXRoleSelector组件 main/manager-web/src/components/PromptXRoleSelector.vue
- [X] T020 [P] [US1] 创建Vuex状态管理模块 main/manager-web/src/store/modules/promptxAgent.js
- [X] T021 [P] [US1] 定义类型 main/manager-web/src/types/promptx.js (PromptXRole, AgentConfig等,使用JSDoc)
- [x] T022 [US1] 修改roleConfig.vue组件,添加智能体类型选择和条件渲染 main/manager-web/src/views/roleConfig.vue
- [x] T023 [US1] 实现角色选择后自动生成系统提示词逻辑
- [x] T024 [US1] 添加系统提示词只读显示和提示信息
- [x] T025 [US1] 实现PromptX服务不可用时的前端错误提示

### 集成验证 - User Story 1

- [ ] T026 [US1] 端到端测试:创建PromptX智能体完整流程(按quickstart.md测试步骤)
- [ ] T027 [US1] 验证角色列表加载性能(<3秒)
- [ ] T028 [US1] 验证系统提示词生成性能(<100ms)

**Checkpoint**: User Story 1应完全功能性并可独立测试

---

## Phase 4: User Story 2 - 使用PromptX智能体对话 (Priority: P1)

**Goal**: 用户能够直接与PromptX智能体对话,LLM自动执行PromptX认知循环

**Independent Test**:
1. 使用US1创建的PromptX智能体
2. 用户发起对话
3. 验证LLM自动调用promptx_action, recall, remember
4. 检查MCP调用日志验证认知循环

### 实现 - User Story 2

- [ ] T029 [US2] 验证现有对话模块能够正确传递系统提示词到LLM引擎
- [ ] T030 [US2] 验证LLM配置支持function calling (检查模型是否为OpenAI/Claude/GLM-4等)
- [ ] T031 [US2] 测试系统提示词引导LLM执行promptx_action调用
- [ ] T032 [US2] 测试DMN全景扫描: recall(role, null)调用
- [ ] T033 [US2] 测试多轮recall深挖流程
- [ ] T034 [US2] 测试remember保存新知识
- [ ] T035 [US2] 实现MCP工具调用失败时的错误处理(继续对话但记录日志)
- [ ] T036 [US2] 添加对话中PromptX工具调用的详细日志

### 集成验证 - User Story 2

- [ ] T037 [US2] 端到端测试:完整对话流程验证(按quickstart.md测试步骤)
- [ ] T038 [US2] 验证第一条消息触发promptx_action
- [ ] T039 [US2] 验证任务问题触发DMN扫描和多轮recall
- [ ] T040 [US2] 验证对话结束触发remember
- [ ] T041 [US2] 验证第二次对话能够recall之前的记忆
- [ ] T042 [US2] 性能测试:对话响应时间增加不超过2秒

**Checkpoint**: User Stories 1和2都应独立工作

---

## Phase 5: User Story 3 - 查看和管理PromptX智能体配置 (Priority: P2)

**Goal**: 管理员能够查看和编辑PromptX智能体配置,更换角色并重新生成提示词

**Independent Test**:
1. 管理员访问智能体列表
2. 查看PromptX智能体详情(角色ID、名称、系统提示词)
3. 编辑智能体名称
4. 更换角色并验证系统提示词重新生成

### 后端实现 - User Story 3

- [ ] T043 [P] [US3] 实现GET /api/agents/promptx/{id}端点在 main/xiaozhi-server/api/routes/promptx_agent.py
- [ ] T044 [P] [US3] 实现PUT /api/agents/promptx/{id}端点在 main/xiaozhi-server/api/routes/promptx_agent.py
- [ ] T045 [P] [US3] 实现DELETE /api/agents/promptx/{id}端点在 main/xiaozhi-server/api/routes/promptx_agent.py
- [ ] T046 [US3] 实现智能体配置查询逻辑,区分PromptX和普通智能体
- [ ] T047 [US3] 实现角色更换时自动重新生成系统提示词逻辑
- [ ] T048 [US3] 添加角色不存在的检测和异常标识

### 前端实现 - User Story 3

- [ ] T049 [P] [US3] 在promptx.js中添加getAgentDetail, updateAgent, deleteAgent方法
- [ ] T050 [US3] 修改智能体列表页面,清晰标识PromptX智能体类型
- [ ] T051 [US3] 实现智能体编辑页面的PromptX字段展示(名称可编辑、角色可更换、系统提示词只读)
- [ ] T052 [US3] 实现角色更换时触发系统提示词重新生成
- [ ] T053 [US3] 添加"配置异常"状态标识(角色已被删除)

### 集成验证 - User Story 3

- [ ] T054 [US3] 端到端测试:查看PromptX智能体详情
- [ ] T055 [US3] 端到端测试:编辑智能体名称和其他字段
- [ ] T056 [US3] 端到端测试:更换角色并验证系统提示词更新
- [ ] T057 [US3] 端到端测试:删除PromptX智能体

**Checkpoint**: User Stories 1, 2和3都应独立工作

---

## Phase 6: User Story 4 - PromptX角色列表同步 (Priority: P3)

**Goal**: 管理员能够手动刷新PromptX角色列表,获取最新创建的自定义角色

**Independent Test**:
1. 在PromptX中创建新角色
2. 在智控台点击"刷新角色列表"按钮
3. 验证新角色出现在下拉菜单中

### 后端实现 - User Story 4

- [ ] T058 [US4] 实现角色列表缓存机制(5分钟过期)
- [ ] T059 [US4] 实现POST /api/promptx/roles/refresh端点强制刷新缓存

### 前端实现 - User Story 4

- [ ] T060 [US4] 在PromptXRoleSelector组件中添加"刷新"按钮
- [ ] T061 [US4] 实现刷新按钮点击事件,调用刷新API
- [ ] T062 [US4] 添加刷新中的加载状态提示

### 集成验证 - User Story 4

- [ ] T063 [US4] 端到端测试:刷新角色列表功能

**Checkpoint**: 所有用户故事应独立功能性

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 影响多个用户故事的改进和完善

- [ ] T064 [P] 更新项目README.md,添加PromptX集成说明
- [ ] T065 [P] 更新API文档,添加PromptX相关端点
- [ ] T066 [P] 编写PromptX集成的用户文档(如何创建和使用PromptX智能体)
- [ ] T067 代码审查和清理,移除调试代码
- [ ] T068 性能优化:角色列表分页(如超过50个角色)
- [ ] T069 安全审查:验证PromptX MCP调用的安全性
- [ ] T070 [P] 编写单元测试 main/xiaozhi-server/tests/unit/test_promptx_service.py
- [ ] T071 [P] 编写单元测试 main/xiaozhi-server/tests/unit/test_promptx_template_service.py
- [ ] T072 [P] 编写集成测试 main/xiaozhi-server/tests/integration/test_promptx_mcp_integration.py
- [ ] T073 [P] 编写前端组件测试 main/manager-web/tests/unit/components/PromptXRoleSelector.spec.js
- [ ] T074 按quickstart.md执行完整的开发环境验证流程
- [ ] T075 准备演示数据:创建测试角色和智能体配置

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 可立即开始
- **Foundational (Phase 2)**: 依赖Setup完成 - 阻塞所有用户故事
- **User Stories (Phase 3-6)**: 全部依赖Foundational阶段完成
  - User Stories可以并行进行(如有团队资源)
  - 或按优先级顺序进行(P1 → P1 → P2 → P3)
- **Polish (Phase 7)**: 依赖所有期望的用户故事完成

### User Story Dependencies

- **User Story 1 (P1)**: 可在Foundational后开始 - 无其他故事依赖
- **User Story 2 (P1)**: 可在Foundational后开始 - 依赖US1的数据(但可独立测试)
- **User Story 3 (P2)**: 可在Foundational后开始 - 依赖US1的数据(但可独立测试)
- **User Story 4 (P3)**: 可在Foundational后开始 - 增强US1的功能(但可独立测试)

### 推荐执行顺序

由于US1和US2都是P1优先级且US2依赖US1的配置:

1. **Setup + Foundational** (T001-T009)
2. **User Story 1** (T010-T028) - 完成创建功能
3. **User Story 2** (T029-T042) - 完成对话功能 ⭐ **MVP完整点**
4. **User Story 3** (T043-T057) - 添加管理功能
5. **User Story 4** (T058-T063) - 添加刷新功能
6. **Polish** (T064-T075) - 最终完善

### Within Each User Story

- 后端API端点可并行实现(标记[P])
- 前端组件可并行实现(标记[P])
- 后端实现→前端实现→集成验证

### Parallel Opportunities

- **Phase 1**: T003和T004可并行
- **Phase 2**: T006, T007可并行; T008完成后T009可开始
- **User Story 1**:
  - 后端: T010, T011可并行
  - 前端: T018, T019, T020, T021可并行
- **User Story 3**: T043, T044, T045可并行; T049可并行
- **Polish**: T064, T065, T066, T070, T071, T072, T073可并行

---

## Parallel Example: User Story 1

```bash
# 后端API并行实现:
Task T010: "实现GET /api/promptx/roles端点"
Task T011: "实现POST /api/promptx/generate-prompt端点"

# 前端组件并行实现:
Task T018: "创建PromptX API客户端"
Task T019: "创建PromptXRoleSelector组件"
Task T020: "创建Vuex状态管理模块"
Task T021: "定义TypeScript类型"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

**阶段1: 基础设施** (T001-T009)
- 完成Phase 1: Setup
- 完成Phase 2: Foundational
- **验证**: 数据库字段已添加,实体类已扩展

**阶段2: 创建功能** (T010-T028)
- 完成Phase 3: User Story 1
- **验证**: 可以在智控台创建PromptX智能体
- **可选**: 演示创建流程

**阶段3: 对话功能** (T029-T042)
- 完成Phase 4: User Story 2
- **验证**: 可以与PromptX智能体对话,LLM执行认知循环
- **里程碑**: **完整MVP就绪** - 可部署/演示核心价值

**阶段4: 增强功能** (T043-T063, 可选)
- 添加User Story 3(管理配置)
- 添加User Story 4(刷新列表)

**阶段5: 完善** (T064-T075)
- 测试、文档、优化

### Incremental Delivery

1. **Setup + Foundational** → 基础就绪
2. **+ User Story 1** → 可创建PromptX智能体
3. **+ User Story 2** → 可对话使用(MVP!) 🎯
4. **+ User Story 3** → 可管理配置
5. **+ User Story 4** → 可刷新列表
6. 每个故事增加价值而不破坏之前的故事

### Parallel Team Strategy

如有多个开发者:

**方式1: 分工合作**
1. 团队共同完成Setup + Foundational
2. Foundational完成后:
   - Developer A: User Story 1后端
   - Developer B: User Story 1前端
   - Developer C: 准备测试数据和文档
3. US1完成后:
   - Developer A: User Story 2验证
   - Developer B: User Story 3
   - Developer C: User Story 4

**方式2: 前后端分离**
1. 团队共同完成Setup + Foundational
2. Foundational完成后:
   - Backend Team: US1后端 → US2验证 → US3后端
   - Frontend Team: US1前端 → US3前端 → US4前端
3. 定期集成和联调

---

## Task Count Summary

- **Total Tasks**: 75
- **Setup**: 4 tasks
- **Foundational**: 5 tasks (阻塞性)
- **User Story 1**: 19 tasks (MVP核心)
- **User Story 2**: 14 tasks (MVP核心)
- **User Story 3**: 15 tasks (增强功能)
- **User Story 4**: 6 tasks (增强功能)
- **Polish**: 12 tasks (完善)

**Parallel Opportunities**: 约20个任务可并行执行(标记[P])

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 + Phase 4 = T001-T042 (共42个任务)

---

## Notes

- `[P]` 任务 = 不同文件,无依赖,可并行
- `[Story]` 标签映射任务到特定用户故事,便于追踪
- 每个用户故事应可独立完成和测试
- 在每个checkpoint停止,独立验证故事
- 提交频率:每个任务或逻辑组完成后提交
- 避免:模糊任务、相同文件冲突、破坏独立性的跨故事依赖

## Edge Cases Handling

在实现过程中特别注意处理以下边界场景(来自spec.md):

1. **PromptX服务离线**: 实现优雅降级(T016, T025, T035)
2. **角色不存在**: 配置异常标识(T048, T053)
3. **MCP工具调用失败**: 错误日志但不中断对话(T035, T036)
4. **并发对话**: 验证remember不冲突(T041)
5. **超长对话**: 保持认知循环执行(T036)
6. **空白记忆网络**: 正常回答并开始构建(T032, T034)