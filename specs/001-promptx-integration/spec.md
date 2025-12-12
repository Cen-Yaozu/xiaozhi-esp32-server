# Feature Specification: PromptX智能体集成

**Feature Branch**: `001-promptx-integration`
**Created**: 2025-12-02
**Status**: Draft
**Input**: 在智控台集成PromptX角色管理系统,支持自动激活角色和动态记忆更新

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 创建PromptX智能体 (Priority: P1)

作为系统管理员,我想在智控台创建一个集成PromptX角色的智能体,这样用户就能直接使用专业AI角色而无需在对话中手动激活。

**Why this priority**: 这是整个功能的核心基础,没有创建功能就无法使用PromptX集成。用户能够体验到PromptX专业角色的价值。

**Independent Test**: 可以独立测试创建流程 - 管理员访问智控台,选择"PromptX智能体"类型,从角色列表中选择一个角色(如"产品经理"),填写智能体名称,保存配置,验证配置成功保存到数据库。

**Acceptance Scenarios**:

1. **Given** 管理员登录智控台并进入智能体配置页面, **When** 选择创建新智能体并选择类型为"PromptX智能体", **Then** 系统显示PromptX角色选择下拉菜单
2. **Given** 智能体类型选择为"PromptX智能体", **When** 点击角色选择下拉菜单, **Then** 系统显示所有可用的PromptX角色列表(包括角色名称和描述)
3. **Given** 已选择PromptX角色, **When** 填写智能体名称并点击保存, **Then** 系统生成标准化的系统提示词模板,将角色信息填充到模板变量中,并保存配置
4. **Given** PromptX服务不可用, **When** 尝试加载角色列表, **Then** 系统显示友好的错误提示,建议用户检查PromptX服务状态

---

### User Story 2 - 使用PromptX智能体对话 (Priority: P1)

作为终端用户,我想直接与PromptX智能体对话,系统应该自动激活对应的PromptX角色,这样我就能获得专业的帮助而不需要了解技术细节。

**Why this priority**: 这是用户最终体验的价值所在,如果用户无法与智能体正常对话,整个功能就失去意义。

**Independent Test**: 创建一个PromptX智能体(使用P1创建的配置),用户发起对话,验证LLM自动调用promptx_action激活角色,并在后续对话中正确执行recall和remember操作。可通过查看MCP调用日志验证。

**Acceptance Scenarios**:

1. **Given** 用户选择了一个PromptX智能体, **When** 发送第一条消息, **Then** LLM自动调用promptx_action激活对应角色,并基于角色身份回复用户
2. **Given** 用户提出一个需要专业知识的问题, **When** LLM处理该问题, **Then** LLM首先执行recall(role, null)进行DMN全景扫描,然后根据返回的记忆网络进行多轮recall深挖,最后基于记忆提供专业回答
3. **Given** 对话进行中, **When** 对话结束或LLM回答了用户问题, **Then** LLM自动执行remember保存关键知识点到PromptX记忆网络
4. **Given** 用户在同一智能体进行第二次对话, **When** 提出与之前相关的问题, **Then** LLM能够recall到之前remember的记忆内容,提供连贯的对话体验

---

### User Story 3 - 查看和管理PromptX智能体配置 (Priority: P2)

作为系统管理员,我想查看和编辑已创建的PromptX智能体配置,了解每个智能体使用的角色和系统提示词,必要时进行调整。

**Why this priority**: 提供配置管理能力,让管理员能够维护和优化智能体配置,但不是初始MVP的必要功能。

**Independent Test**: 管理员访问智能体列表,查看PromptX智能体的配置详情,可以看到关联的角色ID、角色名称、系统提示词内容。可以编辑智能体名称但不能修改系统提示词模板(保证认知循环的正确性)。

**Acceptance Scenarios**:

1. **Given** 管理员在智能体列表页面, **When** 查看PromptX类型的智能体, **Then** 系统清晰标识该智能体的类型为"PromptX智能体",并显示关联的角色名称
2. **Given** 管理员点击编辑PromptX智能体, **When** 进入编辑页面, **Then** 系统显示智能体名称(可编辑)、关联角色(可更换)、系统提示词(只读展示,带说明信息)
3. **Given** 管理员想要更换智能体的PromptX角色, **When** 在编辑页面选择新的角色, **Then** 系统重新生成系统提示词模板并更新配置

---

### User Story 4 - PromptX角色列表同步 (Priority: P3)

作为系统管理员,我想手动刷新PromptX角色列表,确保能够使用最新创建的自定义角色。

**Why this priority**: 提升用户体验,但可以通过重新打开配置页面实现相同效果,不是核心功能。

**Independent Test**: 在PromptX中创建新角色后,在智控台点击"刷新角色列表"按钮,验证新角色出现在下拉菜单中。

**Acceptance Scenarios**:

1. **Given** PromptX服务中新增了自定义角色, **When** 管理员在角色选择器旁点击刷新按钮, **Then** 系统重新调用promptx_discover工具获取最新角色列表
2. **Given** 刷新过程中, **When** PromptX服务响应缓慢, **Then** 系统显示加载状态,避免用户重复点击

---

### Edge Cases

- **PromptX服务离线**: 用户尝试使用PromptX智能体对话时,如果PromptX MCP服务不可用,LLM应该优雅降级到普通对话模式,并向用户说明当前无法使用专业角色功能
- **角色不存在**: 如果智能体配置中的角色ID在PromptX中已被删除,系统应该在智能体列表中标识该智能体为"配置异常",并在使用时提示管理员重新配置
- **MCP工具调用失败**: LLM执行recall或remember时如果MCP工具返回错误,应该继续对话但记录错误日志,不应该中断用户体验
- **并发对话场景**: 同一PromptX角色被多个用户同时使用时,每个用户的remember操作应该正确保存到该角色的记忆网络,不产生冲突
- **超长对话**: 对话轮次过多导致上下文过长时,系统应该保持PromptX认知循环的执行(特别是remember操作),避免因为上下文限制而丢失记忆保存
- **空白记忆网络**: 新创建的PromptX角色没有任何记忆时,recall(null)返回空网络,LLM应该能够正常回答并通过remember开始构建记忆网络

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统必须在智控台的智能体类型选择中提供"PromptX智能体"选项
- **FR-002**: 系统必须通过调用PromptX的discover工具获取所有可用角色列表(包括系统级、项目级和用户级角色)
- **FR-003**: 系统必须为每个PromptX角色显示角色名称、角色ID和角色描述信息
- **FR-004**: 系统必须使用标准化的系统提示词模板,并自动填充角色变量(ROLE_ID、ROLE_NAME、ROLE_DESCRIPTION)
- **FR-005**: 系统提示词模板必须引导LLM执行完整的PromptX认知循环:对话开始时激活角色 → 任务时DMN扫描 → 多轮recall深挖 → 回答 → remember保存
- **FR-006**: 系统必须将生成的系统提示词与智能体配置一起保存到数据库
- **FR-007**: 系统必须在智能体列表中清晰标识PromptX智能体类型,区别于普通智能体
- **FR-008**: 系统必须允许管理员查看PromptX智能体的完整系统提示词内容(只读)
- **FR-009**: 系统必须允许管理员更换PromptX智能体关联的角色,并自动重新生成系统提示词
- **FR-010**: 当PromptX MCP服务不可用时,系统必须在创建智能体时显示明确的错误提示,引导用户检查服务状态
- **FR-011**: 系统必须验证PromptX MCP服务的URL配置正确(从配置文件读取, 默认为 http://127.0.0.1:5203/mcp)
- **FR-012**: LLM运行时必须能够访问PromptX MCP工具(action、recall、remember、discover)
- **FR-013**: 系统必须记录PromptX工具调用日志,便于调试和问题排查

### Non-Functional Requirements

- **NFR-001**: 角色列表加载时间应在3秒内完成(正常网络条件下)
- **NFR-002**: 系统提示词生成应该是即时的(小于100毫秒)
- **NFR-003**: PromptX智能体的对话响应时间不应因为recall操作显著增加(相比普通智能体,增加不超过2秒)

### Key Entities

- **PromptXAgent(PromptX智能体)**:
  - 智能体类型标识: "promptx"
  - 关联角色ID: PromptX角色的唯一标识符
  - 关联角色名称: 角色的显示名称
  - 关联角色描述: 角色的功能描述
  - 系统提示词: 基于模板生成的完整提示词
  - 其他通用智能体属性: 名称、创建时间、更新时间等

- **PromptXRole(PromptX角色)**:
  - 角色ID: 唯一标识符(如 product-manager)
  - 角色名称: 显示名称(如 产品经理)
  - 角色描述: 功能描述
  - 角色来源: system(系统级) | project(项目级) | user(用户级)

- **SystemPromptTemplate(系统提示词模板)**:
  - 模板内容: 包含变量占位符的Markdown文本
  - 支持的变量: {{ROLE_ID}}, {{ROLE_NAME}}, {{ROLE_DESCRIPTION}}

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 管理员能够在3分钟内完成一个PromptX智能体的创建配置流程
- **SC-002**: 用户与PromptX智能体对话时,90%的会话能够成功激活PromptX角色(通过MCP调用日志验证)
- **SC-003**: PromptX智能体的对话中,LLM在80%的任务场景下会执行DMN扫描(recall with null)
- **SC-004**: 对话结束时,LLM在75%的会话中会执行remember操作保存新知识
- **SC-005**: 用户在同一智能体的第二次对话中,能够体验到基于记忆的连贯对话(通过用户反馈或A/B测试验证)
- **SC-006**: PromptX服务不可用时,系统能够在100%的场景下提供明确的错误提示,避免用户困惑
- **SC-007**: 系统能够支持至少50个PromptX角色的列表展示和选择,不出现性能问题

## Assumptions

- PromptX MCP服务已经在本地正确安装和配置,运行在 http://127.0.0.1:5203/mcp
- 系统已经正确配置了PromptX MCP服务连接信息(在mcp_server_settings.json中)
- LLM模型支持MCP工具调用(如OpenAI、Claude等支持function calling的模型)
- 智控台前端使用Vue.js框架(基于现有codebase)
- 后端使用Python FastAPI框架(基于现有codebase)
- 数据库使用MySQL存储智能体配置
- 系统提示词模板存储为静态文件或配置项,不需要动态修改
- PromptX角色的认知循环逻辑已经在PromptX服务端正确实现
- 用户有基本的AI对话使用经验,了解智能体的概念

## Dependencies

- **外部服务依赖**: PromptX MCP服务必须运行在 http://127.0.0.1:5203/mcp
- **MCP协议依赖**: 系统使用streamable-http传输模式与PromptX通信
- **前端组件依赖**: 需要修改现有的roleConfig.vue组件,增加PromptX智能体类型支持
- **后端API依赖**: 需要新增获取PromptX角色列表的API端点
- **模板依赖**: 需要创建并维护系统提示词模板文件

## Scope Boundaries

### In Scope
- 智控台UI支持创建、查看、编辑PromptX智能体
- 系统提示词模板的设计和变量替换逻辑
- PromptX角色列表的获取和展示
- PromptX智能体与现有智能体系统的集成
- 基本的错误处理和用户提示
- MCP工具调用日志记录

### Out of Scope
- PromptX角色的创建和管理(这是PromptX平台的功能,不在本项目范围)
- PromptX MCP服务的安装和配置(假设已完成)
- 系统提示词模板的可视化编辑器(使用静态模板)
- PromptX认知循环的优化或修改(使用PromptX官方设计)
- 记忆网络的可视化展示(可作为未来增强功能)
- 多语言支持(当前仅支持中文)
- PromptX智能体的使用统计和分析(可作为未来增强功能)
- 离线模式支持(PromptX服务必须在线)

## Open Questions

无 - 规格说明已完整定义所有关键需求
