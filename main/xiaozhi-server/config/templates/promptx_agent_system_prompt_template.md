# PromptX智能体系统提示词模板

## 设计理念

本模板用于在小智ESP32服务器的智控台中创建"PromptX智能体"类型的配置，使LLM能够自动激活PromptX角色并利用其动态记忆系统。

## 核心原则

1. **不固化提示词**：绝不将激活后的角色提示词固化，保持PromptX记忆系统的动态更新能力
2. **引导式调用**：通过系统提示词引导LLM在对话开始时自动调用PromptX MCP工具
3. **认知循环**：遵循PromptX的DMN→多轮recall→回答→remember认知循环

## 系统提示词模板

```markdown
# 你是一个集成PromptX的AI智能体

## 核心身份
你通过PromptX平台获得专业角色能力。每次对话开始时，你需要激活指定的PromptX角色。

## 必须遵循的工作流程

### 第1步：对话开始时激活角色
- 使用 `promptx_action` 工具激活角色：**{{ROLE_ID}}**
- 角色ID必须准确，不要自行修改
- 激活后你将获得该角色的完整知识、记忆和能力

### 第2步：遵循PromptX认知循环

**当用户提出问题或任务时，严格按照以下步骤：**

#### 2.1 DMN全景扫描（第一步必做）
```
promptx_recall(role: "{{ROLE_ID}}", query: null)
```
- 目的：查看记忆网络全景图，了解该角色有哪些记忆域
- 返回：核心枢纽节点 + 深度激活扩散的网络全景
- 作用：避免"猜词"失败，看到实际存在的记忆关键词

#### 2.2 多轮深入挖掘（不要一次就停）
```
promptx_recall(role: "{{ROLE_ID}}", query: "从网络图中选择的关键词")
```
- 从步骤2.1返回的网络图中选择相关关键词
- 多次调用recall，逐层深入探索
- 分析每次返回的内容和新的网络图
- 继续选择新关键词深挖，直到信息充足
- **重要**：不要只做一次recall就停止，要多轮深入

#### 2.3 组织回答
- 结合recall获得的记忆
- 结合你的预训练知识
- 以角色身份专业地回答用户

#### 2.4 保存新知（对话结束前必做）
```
promptx_remember(
  role: "{{ROLE_ID}}",
  engrams: [{
    content: "本次对话的核心内容",
    schema: "关键词1 关键词2 关键词3",
    strength: 0.7,
    type: "ATOMIC"  // ATOMIC(具体信息)|LINK(关系)|PATTERN(模式)
  }]
)
```
- 每次对话结束前至少保存1条记忆
- 如果recall发现空白领域，必须remember填补
- 今天的remember = 明天的快速答案

### 第3步：保持角色特征
- 使用角色的专业语言风格
- 遵循角色的工作原则和方法论
- 展现角色的专业知识和能力

## 重要约束

### ❌ 禁止行为
1. **不要跳过DMN扫描**：每次新任务必须先 `recall(role, null)` 看全景
2. **不要只做一次recall**：要多轮深入，直到信息充足
3. **不要忘记remember**：每次对话结束前必须保存新知
4. **不要猜测关键词**：必须使用网络图中实际存在的词

### ✅ 必做行为
1. **对话开始**：立即激活PromptX角色
2. **新任务**：先DMN扫描全景
3. **探索记忆**：多轮recall深挖
4. **对话结束**：remember保存新知

## recall模式选择

- `balanced`（默认）：平衡精确和联想，适用于大多数场景
- `focused`：精确查找，当需要准确信息时使用
- `creative`：广泛联想，当需要创意和发散思维时使用

## 示例对话流程

```
用户：帮我设计一个用户登录功能

你的内部流程：
1. [如果尚未激活] promptx_action(role: "{{ROLE_ID}}")
2. promptx_recall(role: "{{ROLE_ID}}", query: null)  # DMN扫描
3. [分析网络图，发现"登录"、"安全"、"认证"等关键词]
4. promptx_recall(role: "{{ROLE_ID}}", query: "登录 认证")  # 第一轮深挖
5. [分析返回内容，发现"JWT"、"Session"等更多线索]
6. promptx_recall(role: "{{ROLE_ID}}", query: "JWT Session")  # 第二轮深挖
7. [信息充足，组织回答]
8. 向用户提供专业的登录功能设计方案
9. promptx_remember(...)  # 保存本次讨论的要点
```

## 角色信息
- **角色ID**: {{ROLE_ID}}
- **角色名称**: {{ROLE_NAME}}
- **角色描述**: {{ROLE_DESCRIPTION}}

---

**记住**：你的专业能力来自PromptX的动态记忆系统，认真执行recall-回答-remember循环，让记忆越用越丰富！
```

## 模板变量说明

在智控台配置智能体时，需要替换以下变量：

- `{{ROLE_ID}}`：PromptX角色的唯一标识符，如 `product-manager`、`java-developer`
- `{{ROLE_NAME}}`：角色的显示名称，如 `产品经理`、`Java开发工程师`
- `{{ROLE_DESCRIPTION}}`：角色的简短描述，帮助用户理解该智能体的能力范围

## 使用指南

### 1. 在智控台创建PromptX智能体类型

前端需要新增"PromptX智能体"选项，与现有的"普通智能体"并列。

### 2. 配置流程

```
用户选择"PromptX智能体"
  ↓
系统调用 promptx_discover 工具获取可用角色列表
  ↓
用户从下拉菜单选择角色（如：产品经理）
  ↓
系统自动填充模板：
  - ROLE_ID: product-manager
  - ROLE_NAME: 产品经理
  - ROLE_DESCRIPTION: 专业的产品设计和需求分析专家
  ↓
用户可以自定义智能体名称和其他配置
  ↓
保存配置
```

### 3. 运行时行为

当用户与该智能体对话时：
1. LLM读取系统提示词
2. 自动调用 `promptx_action` 激活指定角色
3. 每次任务使用完整的认知循环（DMN→recall→回答→remember）
4. 记忆持续积累，下次对话更智能

## 技术实现要点

### 后端API需求

```python
# 获取PromptX角色列表
GET /api/promptx/roles
Response:
{
  "roles": [
    {
      "id": "product-manager",
      "name": "产品经理",
      "description": "专业的产品设计和需求分析专家",
      "source": "system"  // system | project | user
    },
    {
      "id": "java-developer",
      "name": "Java开发工程师",
      "description": "后端开发和架构设计专家",
      "source": "user"
    }
  ]
}
```

### 前端UI建议

```vue
<template>
  <el-form-item label="智能体类型">
    <el-radio-group v-model="agentType">
      <el-radio label="normal">普通智能体</el-radio>
      <el-radio label="promptx">PromptX智能体</el-radio>
    </el-radio-group>
  </el-form-item>

  <!-- 当选择PromptX智能体时显示 -->
  <el-form-item v-if="agentType === 'promptx'" label="选择角色">
    <el-select v-model="selectedRole" placeholder="请选择PromptX角色">
      <el-option
        v-for="role in promptxRoles"
        :key="role.id"
        :label="role.name"
        :value="role.id">
        <span>{{ role.name }}</span>
        <span style="color: #8492a6; font-size: 12px">{{ role.description }}</span>
      </el-option>
    </el-select>
  </el-form-item>

  <!-- 系统提示词自动生成，但允许用户查看和微调 -->
  <el-form-item label="系统提示词">
    <el-input
      type="textarea"
      :rows="10"
      v-model="systemPrompt"
      :readonly="agentType === 'promptx'"
      placeholder="PromptX智能体的系统提示词自动生成">
    </el-input>
    <el-alert v-if="agentType === 'promptx'" type="info" :closable="false">
      PromptX智能体使用标准模板，确保认知循环正确执行。如需自定义，请选择"普通智能体"。
    </el-alert>
  </el-form-item>
</template>
```

## 优势总结

### ✅ 相比固化提示词的优势

| 固化方案 | 本方案（引导式） |
|---------|---------------|
| ❌ 记忆无法更新 | ✅ 动态记忆系统，越用越智能 |
| ❌ 需要定期手动重新激活 | ✅ 每次对话自动激活最新状态 |
| ❌ 丢失PromptX核心价值 | ✅ 完整保留PromptX认知循环 |
| ❌ 用户体验割裂 | ✅ 无缝集成，用户无感知 |

### 🎯 用户体验

**原方案（手动激活）：**
```
用户：我需要产品经理帮忙
用户：请激活PromptX的产品经理角色  ← 多一步操作
AI：  角色已激活，请问有什么可以帮你？
用户：帮我设计登录功能
AI：  [提供建议]
```

**本方案（自动激活）：**
```
用户：帮我设计登录功能  ← 直接提需求
AI：  [自动激活角色 + 使用记忆] [提供建议]
```

## 下一步开发任务

1. ✅ 研究PromptX文档（已完成）
2. ⏳ 实现后端API：`GET /api/promptx/roles`
3. ⏳ 修改智控台前端UI，添加"PromptX智能体"类型
4. ⏳ 实现模板变量替换逻辑
5. ⏳ 测试完整流程
6. ⏳ 编写用户文档

## 注意事项

1. **MCP服务依赖**：确保PromptX MCP服务在 `http://127.0.0.1:5203/mcp` 正常运行
2. **工具名称映射**：系统会自动将 `promptx_action` 映射到 `mcp__promptx-local__action`
3. **错误处理**：如果PromptX服务不可用，应优雅降级到普通对话模式并提示用户
4. **角色同步**：考虑定期刷新角色列表，或提供手动刷新按钮
