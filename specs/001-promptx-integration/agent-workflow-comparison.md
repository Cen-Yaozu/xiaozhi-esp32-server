# Normal Agent vs PromptX Agent 工作流程对比分析

## 1. Normal Agent 工作流程（原始小智）

### 1.1 初始化流程

```
WebSocket连接建立
    ↓
handle_connection()
    ↓
_background_initialize() (异步，不阻塞)
    ├── _initialize_private_config_async() - 从API获取设备配置
    └── _initialize_components() - 在线程池中初始化组件
            ├── 【第1步：快速初始化】
            │   └── get_quick_prompt(user_prompt)
            │       ├── 检查设备缓存: cache["device_prompt:{device_id}"]
            │       └── 直接返回用户配置的提示词
            │       └── change_system_prompt(prompt)
            │           └── dialogue.update_system_message(prompt)
            │
            ├── 初始化 VAD/ASR/TTS
            ├── 初始化声纹识别
            ├── 初始化记忆模块
            ├── 初始化意图识别
            │
            └── 【第2步：增强提示词】
                └── _init_prompt_enhancement()
                    ├── update_context_info() - 更新上下文信息
                    └── build_enhanced_prompt()
                        ├── 使用Jinja2模板渲染
                        ├── 注入动态上下文：
                        │   ├── base_prompt (用户提示词)
                        │   ├── today_date (今天日期)
                        │   ├── today_weekday (星期几)
                        │   ├── lunar_date (农历)
                        │   ├── local_address (位置，从IP解析，缓存)
                        │   ├── weather_info (天气，缓存)
                        │   └── dynamic_context (上下文源数据)
                        └── change_system_prompt(enhanced_prompt)
```

### 1.2 对话流程

```
用户发送音频
    ↓
ASR识别 → 文本query
    ↓
chat(query, depth=0)
    ├── dialogue.put(Message(role="user", content=query))
    ├──
    ├── 【记忆检索】
    │   └── memory.query_memory(query) - 检索相关记忆
    │
    ├── 【LLM推理】
    │   └── llm.response(session_id, dialogue_with_memory)
    │       ├── 输入：系统提示词 + 历史对话 + 记忆 + 用户问题
    │       └── 输出：流式响应
    │
    ├── 【工具调用】（如果启用function_call）
    │   └── func_handler.execute_tool()
    │       └── chat(tool_result, depth+1) - 递归调用
    │
    └── 【TTS合成】
        └── 流式输出音频
```

### 1.3 系统提示词管理

**PromptManager核心机制：**

1. **快速初始化路径**（不阻塞连接）
   - 使用用户配置的原始提示词
   - 设备级缓存 `device_prompt:{device_id}`
   - 立即可用，延迟 < 50ms

2. **异步增强路径**（后台执行）
   - 使用Jinja2模板系统
   - 注入动态上下文（时间、位置、天气等）
   - 多级缓存策略：
     - `CONFIG`: 配置文件、模板（不自动过期）
     - `DEVICE_PROMPT`: 设备提示词（不自动过期）
     - `LOCATION`: IP位置信息（1小时过期）
     - `WEATHER`: 天气信息（30分钟过期）

3. **模板变量**
   ```jinja2
   你是{{base_prompt}}

   当前时间：{{today_date}} {{today_weekday}} {{lunar_date}}
   当前位置：{{local_address}}
   天气：{{weather_info}}

   {{dynamic_context}}
   ```

---

## 2. PromptX Agent 工作流程（当前实现）

### 2.1 前端配置流程

```
用户在管理后台选择角色
    ↓
roleConfig.vue
    ├── 选择 agentType = "promptx"
    ├── PromptXRoleSelector 组件
    │   └── 显示角色列表（从后端API获取）
    └── handlePromptXRoleChange(roleData)
        ├── 调用 API: /api/promptx/generate-system-prompt
        │   ├── 参数：roleId, roleName, roleDescription
        │   └── 返回：生成的系统提示词（只读）
        └── form.systemPrompt = 生成的提示词
            └── 保存到数据库
```

### 2.2 后端系统提示词生成

```
POST /api/promptx/generate-system-prompt
    ↓
promptx_handler.handle_generate_prompt()
    ↓
template_service.generate_system_prompt(roleId, roleName, roleDescription)
    ├── 加载模板：promptx_agent_system_prompt_template.md
    └── 替换模板变量：
        ├── {{ROLE_ID}}
        ├── {{ROLE_NAME}}
        └── {{ROLE_DESCRIPTION}}
    └── 返回完整的工作流指令（~2000 tokens）
```

**生成的系统提示词内容：**
```
你现在是 **{{ROLE_NAME}}**
{{ROLE_DESCRIPTION}}

### 第1步：对话开始时激活角色
使用 `promptx_action` 工具激活角色：**{{ROLE_ID}}**

### 第2步：遵循PromptX认知循环
#### 2.1 DMN全景扫描（第一步必做）
promptx_recall(role: "{{ROLE_ID}}", query: null)

#### 2.2 多轮深入挖掘（不要一次就停）
promptx_recall(role: "{{ROLE_ID}}", query: "关键词")
[重复多次]

#### 2.3 生成回答

### 第3步：对话后保存新记忆
promptx_remember(role: "{{ROLE_ID}}", engrams: [...])
```

### 2.3 运行时流程

```
WebSocket连接建立
    ↓
_initialize_components()
    ├── get_quick_prompt(用户的promptx提示词)
    │   └── 这个提示词包含完整的工作流指令（~2000 tokens）
    └── change_system_prompt(prompt)

用户发送第一条消息
    ↓
LLM看到系统提示词中的指令
    ↓
【第1步】执行 promptx_action
    ├── MCP调用：mcp__promptx-local__action(role="luban")
    └── 返回：角色文档 + 记忆网络统计 (~12,690 tokens)
        ├── 角色完整文档
        ├── 思维模式定义
        ├── 行为准则
        └── 记忆网络统计（156节点，89记忆）

【第2步】执行 promptx_recall(null) - DMN扫描
    ├── MCP调用：mcp__promptx-local__recall(query=null)
    └── 返回：思维导图 + 49个关键词

【第3步】执行 promptx_recall(关键词) - 深入挖掘
    ├── MCP调用：mcp__promptx-local__recall(query="Bridge模式 dry-run测试")
    └── 返回：4条具体记忆片段（74天前，强度0.8-0.9）

【第4步】LLM生成回答
    └── 基于角色文档 + 记忆 + 用户问题

【第5步】执行 promptx_remember
    ├── MCP调用：mcp__promptx-local__remember(engrams=[...])
    └── 保存新记忆到知识网络
```

---

## 3. 详细对比

### 3.1 系统提示词Token消耗

| 类型 | 初始化 | 运行时增量 | 总计 |
|------|--------|-----------|------|
| **Normal Agent** | ~500-1000 tokens | 0 | ~500-1000 tokens |
| **PromptX Agent** | ~2000 tokens（工作流指令） | ~12,690 tokens（action返回） | **~14,690 tokens** |

### 3.2 首次响应延迟

| 类型 | 第一步 | 第二步 | 第三步 | 总延迟 |
|------|--------|--------|--------|--------|
| **Normal Agent** | 快速初始化（<50ms） | 记忆检索（100-300ms） | LLM推理（2-5s） | **2-5秒** |
| **PromptX Agent** | action调用（3-5s） | DMN扫描（2-3s） | 关键词挖掘（2-3s × N轮） | **9-15秒** |

### 3.3 Token效率对比

**Normal Agent每次对话的Token使用：**
```
系统提示词：500-1000 tokens
历史对话：1000-3000 tokens
记忆检索：200-500 tokens
用户问题：50-200 tokens
---------------------------------
总计：1750-4700 tokens
```

**PromptX Agent每次对话的Token使用：**
```
系统提示词：2000 tokens
action返回：12,690 tokens
DMN扫描：500-1000 tokens
关键词挖掘：1000-2000 tokens × N轮
历史对话：1000-3000 tokens
用户问题：50-200 tokens
---------------------------------
总计：17,240-23,890 tokens（首次）
总计：5,550-8,200 tokens（后续，如果不重复action）
```

### 3.4 功能对比

| 功能 | Normal Agent | PromptX Agent | 说明 |
|------|--------------|---------------|------|
| **提示词来源** | 用户手动配置 | PromptX角色库 | PromptX提供专业预设角色 |
| **动态上下文** | ✅ Jinja2模板注入 | ❌ 未集成 | Normal Agent注入时间、位置、天气 |
| **记忆管理** | ✅ Memory模块 | ✅ PromptX记忆网络 | PromptX使用图结构记忆网络 |
| **提示词增强** | ✅ 异步增强 | ❌ 静态模板 | Normal Agent后台增强，不阻塞 |
| **设备缓存** | ✅ 多级缓存 | ❌ 未实现 | Normal Agent缓存位置、天气等 |
| **首次延迟** | 2-5秒 | 9-15秒 | PromptX认知循环较慢 |
| **Token效率** | 高（1750-4700） | 低（17,240-23,890首次） | PromptX消耗大量Token |
| **角色一致性** | 中等 | 高 | PromptX角色文档更完整 |
| **专业性** | 依赖用户编写 | 高 | PromptX提供专业角色 |

---

## 4. 核心问题分析

### 4.1 Token浪费严重

**问题：**
- 每次对话都需要执行完整的认知循环
- action返回12,690 tokens的角色文档（大部分已在系统提示词中）
- DMN扫描返回大量不相关的关键词

**原因：**
- 系统提示词模板要求"每次对话必做"认知循环
- 没有智能判断机制跳过不必要的步骤

### 4.2 延迟过高影响用户体验

**问题：**
- 首次响应需要9-15秒
- 简单问题也要走完整流程

**原因：**
- 串行执行：action → recall(null) → recall(keywords) → answer
- 没有快速路径处理简单问题

### 4.3 未利用Normal Agent的优势

**问题：**
- 没有集成Jinja2动态上下文
- 没有使用多级缓存系统
- 没有实现快速初始化 + 异步增强机制

**原因：**
- PromptX集成是独立实现的
- 没有复用PromptManager的基础设施

### 4.4 认知循环过于刚性

**问题：**
- 模板强制要求"多轮深入挖掘（不要一次就停）"
- 简单问题也要执行复杂认知循环

**原因：**
- 系统提示词是静态模板，没有条件判断
- LLM需要严格遵循指令，无法灵活调整

---

## 5. 优化方向

### 5.1 短期优化（快速见效）

**1. 精简action返回内容**
- 当前：返回完整角色文档（12,690 tokens）
- 优化：只返回核心身份标识（500 tokens）
- 原因：完整文档已在系统提示词中

**2. 智能认知循环**
```python
def should_use_cognitive_loop(query: str) -> bool:
    """判断是否需要完整认知循环"""
    # 简单问题：打招呼、简单事实查询
    if is_simple_query(query):
        return False

    # 复杂问题：需要深度思考、多步推理
    if is_complex_query(query):
        return True

    # 默认：快速路径
    return False
```

**3. 预激活机制**
```python
async def _background_initialize():
    # 在后台预先激活角色
    if agent_type == "promptx":
        asyncio.create_task(pre_activate_role(role_id))
```

### 5.2 中期优化（架构改进）

**1. 分层系统提示词**
```
[基础层] 用户配置的角色信息（500 tokens）
    ↓
[动态层] Jinja2模板注入上下文（200 tokens）
    ↓
[认知层] 按需插入工作流指令（0-1000 tokens）
```

**2. 集成PromptManager**
```python
class PromptXEnhancedManager(PromptManager):
    def build_promptx_prompt(self, role_id, device_id, client_ip):
        # 复用Normal Agent的增强逻辑
        base_prompt = self.get_promptx_role_prompt(role_id)
        enhanced_prompt = self.build_enhanced_prompt(
            base_prompt, device_id, client_ip
        )
        return enhanced_prompt
```

**3. 可选认知模式**
```python
cognitive_modes = {
    "full": "完整认知循环（action+recall+remember）",
    "smart": "智能判断（按需调用）",
    "fast": "快速模式（只action）",
}
```

### 5.3 长期优化（体验提升）

**1. 流式认知循环**
- 边执行action边开始LLM推理
- 使用Server-Sent Events流式返回中间结果

**2. 记忆预取**
- 在用户说话时（VAD检测到语音）就开始预取记忆
- 减少等待时间

**3. 自适应工作流**
- LLM自主决定是否需要recall
- 不再强制要求"多轮深入挖掘"

---

## 6. 推荐实施方案

### Phase 1: 立即优化（1-2天）
1. ✅ 修改promptx_agent_system_prompt_template.md
   - 删除"多轮深入挖掘（不要一次就停）"
   - 改为"根据需要灵活调用recall"

2. ✅ 添加简单问题判断
   ```python
   SIMPLE_PATTERNS = ["你好", "在吗", "天气怎么样"]
   if any(p in query for p in SIMPLE_PATTERNS):
       skip_cognitive_loop = True
   ```

3. ✅ 预激活角色
   - 在_background_initialize中异步调用action
   - 缓存action结果

### Phase 2: 架构优化（3-5天）
1. PromptXEnhancedManager集成
2. 分层系统提示词
3. 智能认知循环判断

### Phase 3: 体验优化（1-2周）
1. 流式认知循环
2. 记忆预取
3. 自适应工作流

---

## 7. 预期效果

| 指标 | 当前 | Phase 1 | Phase 2 | Phase 3 |
|------|------|---------|---------|---------|
| **首次响应（简单）** | 9-15秒 | 3-5秒 | 2-4秒 | 1-3秒 |
| **首次响应（复杂）** | 9-15秒 | 8-12秒 | 6-10秒 | 5-8秒 |
| **Token消耗（首次）** | 17,240 | 8,000 | 5,500 | 5,000 |
| **Token消耗（后续）** | 5,550 | 3,000 | 2,500 | 2,000 |
| **用户体验** | 较慢 | 改善 | 良好 | 优秀 |

---

## 8. 总结

**Normal Agent的优势：**
- ✅ 快速初始化 + 异步增强
- ✅ 多级缓存系统
- ✅ Jinja2动态上下文注入
- ✅ Token效率高
- ✅ 响应延迟低

**PromptX Agent的优势：**
- ✅ 专业角色库
- ✅ 图结构记忆网络
- ✅ 角色一致性强
- ✅ 认知能力完整

**最佳集成方案：**
将PromptX的角色能力与Normal Agent的基础设施结合，取长补短：
1. 使用PromptX的角色库和记忆网络
2. 复用PromptManager的缓存和增强机制
3. 实现智能认知循环，按需调用工具
4. 保持快速初始化 + 异步增强的架构

这样既能获得专业的角色能力，又能保持良好的用户体验。
