# Technical Research: PromptX智能体集成

**Date**: 2025-12-02
**Feature**: PromptX智能体集成
**Purpose**: 解决实施计划中标识的技术不确定性

## 1. PromptX MCP工具调用模式

### 决策: 使用discover工具获取角色列表

**选择**: 通过MCP调用`promptx_discover`工具,解析Markdown返回结果提取角色信息

**理由**:
- discover工具是PromptX官方提供的资源发现接口
- 返回格式化的资源列表,包含角色ID、名称、描述
- 自动聚合系统级、项目级、用户级三个来源的角色

**替代方案考虑**:
- 直接读取JSON注册表文件 - 被拒绝,因为:
  - 需要知道文件路径(系统级/项目级/用户级)
  - 文件格式可能在PromptX更新时变化
  - 无法利用PromptX的统一发现机制

### discover工具返回格式

**数据结构**:

角色对象包含以下关键字段:

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | string | 角色唯一标识(kebab-case) | `"product-manager"` |
| `source` | string | 资源来源 | `"package"`(系统), `"project"`(项目), `"user"`(用户) |
| `protocol` | string | 资源类型 | `"role"`, `"tool"` 等 |
| `name` | string | 显示名称 | `"产品经理"` |
| `description` | string | 角色功能描述 | `"专业的产品设计和需求分析专家"` |
| `reference` | string | 资源引用路径 | `"@package://resource/role/..."` |

**Markdown返回示例**:

```markdown
📦 **系统角色** (5个)
- `assistant`: 通用助手 → action("assistant")
- `luban`: 鲁班 - PromptX工具开发大师 → action("luban")
- `nuwa`: 女娲 - AI角色创造专家 → action("nuwa")
- `sean`: Sean - 矛盾驱动决策 → action("sean")
- `writer`: Writer - 专业文案写手 → action("writer")

👤 **用户角色** (3个)
- `code-assistant`: Code Assistant 角色 → action("code-assistant")
```

**解析策略**:
- 使用正则表达式提取角色ID和名称
- 通过标题区分角色来源(系统/用户/项目)
- 如需更详细信息,可调用`promptx_action`激活角色查看完整配置

### MCP错误处理策略

**决策**: 实现三层错误处理机制

1. **MCP服务不可用**:
   ```python
   try:
       response = await mcp_client.call_tool("promptx_discover", {})
   except (ConnectionError, TimeoutError) as e:
       logger.error(f"PromptX MCP service unavailable: {e}")
       raise HTTPException(
           status_code=503,
           detail="PromptX服务当前不可用,请检查服务状态或稍后重试"
       )
   ```

2. **工具调用失败**:
   ```python
   if response.get("error"):
       logger.warning(f"PromptX discover failed: {response['error']}")
       return {"roles": [], "error": "无法获取角色列表"}
   ```

3. **前端降级处理**:
   ```javascript
   if (error.status === 503) {
     this.$message.warning('PromptX服务不可用,请使用普通智能体类型')
     this.agentType = 'normal'  // 自动切换回普通模式
   }
   ```

---

## 2. 系统提示词模板设计

### 决策: 使用Markdown文件 + 简单字符串替换

**选择**: 存储为`/core/config/templates/promptx_agent_system_prompt.md`,使用`{{VARIABLE}}`占位符

**理由**:
- Markdown格式清晰易读,方便维护
- 简单的字符串替换性能高,无需模板引擎
- 模板内容来自已有的设计文档(`promptx_agent_system_prompt_template.md`)
- 支持版本控制,可追踪模板变更

**替代方案考虑**:
- Jinja2模板引擎 - 被拒绝,因为:
  - 引入额外依赖
  - 对于简单的变量替换过于复杂
  - 性能不如直接字符串replace
- 存储在数据库 - 被拒绝,因为:
  - 模板内容较长,不适合存储在数据库
  - 需要版本控制和多人协作
  - 配置文件更适合存储静态模板

### 模板变量定义

**支持的变量**:

```python
TEMPLATE_VARIABLES = {
    "ROLE_ID": "product-manager",              # 角色ID
    "ROLE_NAME": "产品经理",                    # 角色显示名称
    "ROLE_DESCRIPTION": "专业的产品设计专家"    # 角色描述
}
```

**替换实现**:

```python
def generate_system_prompt(role_id: str, role_name: str, role_description: str) -> str:
    """生成PromptX智能体的系统提示词"""
    template_path = Path(__file__).parent / "templates" / "promptx_agent_system_prompt.md"

    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # 简单的字符串替换
    prompt = template.replace("{{ROLE_ID}}", role_id)
    prompt = prompt.replace("{{ROLE_NAME}}", role_name)
    prompt = prompt.replace("{{ROLE_DESCRIPTION}}", role_description)

    return prompt
```

**性能考虑**:
- 模板文件约10KB,读取时间<1ms
- 字符串替换操作<1ms
- 总生成时间<5ms,远低于100ms目标

### 模板版本管理

**策略**: 在模板文件头部添加版本标识

```markdown
<!--
  PromptX智能体系统提示词模板
  Version: 1.0.0
  Created: 2025-12-02
  Last Modified: 2025-12-02
-->
```

**升级处理**:
- 模板更新时增加版本号
- 已创建的智能体继续使用原版本提示词(存储在数据库)
- 提供"更新到最新模板"功能(可选)

---

## 3. 数据库模式扩展

### 决策: 扩展现有表结构添加字段

**选择**: 在`ai_agent`和`ai_agent_template`表中添加3个新字段

**理由**:
- 最小侵入性,不改变现有表结构
- 与现有智能体系统集成良好
- 无需创建额外的关联表
- 简化查询逻辑,避免JOIN操作

**替代方案考虑**:
- 创建独立的`ai_agent_promptx`表 - 被拒绝,因为:
  - 增加系统复杂度
  - 需要额外的JOIN查询
  - PromptX特有字段较少(只有3个),不值得单独建表

### 数据库迁移SQL

**`ai_agent`表扩展**:

```sql
-- 添加字段
ALTER TABLE ai_agent
ADD COLUMN agent_type VARCHAR(50) DEFAULT 'normal'
COMMENT '智能体类型: normal(普通智能体)/promptx(PromptX智能体)'
AFTER system_prompt;

ALTER TABLE ai_agent
ADD COLUMN promptx_role_id VARCHAR(100) NULL
COMMENT 'PromptX角色ID,如: product-manager'
AFTER agent_type;

ALTER TABLE ai_agent
ADD COLUMN promptx_role_source VARCHAR(50) NULL
COMMENT 'PromptX角色来源: system/project/user'
AFTER promptx_role_id;

-- 添加索引
CREATE INDEX idx_agent_type ON ai_agent(agent_type);
CREATE INDEX idx_promptx_role ON ai_agent(promptx_role_id);

-- 数据迁移:为现有记录设置默认值
UPDATE ai_agent SET agent_type = 'normal' WHERE agent_type IS NULL;
```

**`ai_agent_template`表扩展** (同样的字段):

```sql
ALTER TABLE ai_agent_template
ADD COLUMN agent_type VARCHAR(50) DEFAULT 'normal'
COMMENT '智能体类型: normal/promptx'
AFTER system_prompt;

ALTER TABLE ai_agent_template
ADD COLUMN promptx_role_id VARCHAR(100) NULL
COMMENT 'PromptX角色ID'
AFTER agent_type;

ALTER TABLE ai_agent_template
ADD COLUMN promptx_role_source VARCHAR(50) NULL
COMMENT 'PromptX角色来源'
AFTER promptx_role_id;

CREATE INDEX idx_template_agent_type ON ai_agent_template(agent_type);

UPDATE ai_agent_template SET agent_type = 'normal' WHERE agent_type IS NULL;
```

### Java实体类扩展

```java
@Data
@TableName("ai_agent")
public class AgentEntity {
    // ... 现有字段

    @Schema(description = "智能体类型: normal(普通智能体)/promptx(PromptX智能体)")
    @TableField("agent_type")
    private String agentType = "normal";

    @Schema(description = "PromptX角色ID")
    @TableField("promptx_role_id")
    private String promptxRoleId;

    @Schema(description = "PromptX角色来源: system/project/user")
    @TableField("promptx_role_source")
    private String promptxRoleSource;
}
```

### 向后兼容性

**保证措施**:
- 新字段允许NULL或有默认值(`agent_type`默认`'normal'`)
- 现有智能体自动标记为`normal`类型
- 现有API和查询逻辑无需修改
- 旧代码不关心新字段,可正常运行

**验证方法**:
```sql
-- 验证所有现有智能体已设置类型
SELECT COUNT(*) FROM ai_agent WHERE agent_type IS NULL;  -- 应返回0

-- 验证PromptX智能体的字段完整性
SELECT * FROM ai_agent
WHERE agent_type = 'promptx'
AND (promptx_role_id IS NULL OR promptx_role_source IS NULL);  -- 应返回空
```

---

## 4. 前端Vue组件集成

### 决策: 修改roleConfig.vue + 新增PromptXRoleSelector组件

**选择**: 在现有配置页面中添加智能体类型选择,条件渲染PromptX角色选择器

**理由**:
- 用户体验统一,无需跳转到新页面
- 复用现有的表单布局和验证逻辑
- 组件化设计,便于维护和测试

**替代方案考虑**:
- 创建独立的PromptX智能体配置页面 - 被拒绝,因为:
  - 用户需要在两个页面之间切换
  - 代码重复(表单验证、提交逻辑等)
  - 增加导航复杂度

### UI组件设计

**roleConfig.vue结构扩展**:

```vue
<template>
  <el-form :model="form" ref="formRef">
    <!-- 新增:智能体类型选择 -->
    <el-form-item label="智能体类型" prop="agentType">
      <el-radio-group v-model="form.agentType">
        <el-radio label="normal">普通智能体</el-radio>
        <el-radio label="promptx">PromptX智能体</el-radio>
      </el-radio-group>
      <el-tag v-if="form.agentType === 'promptx'" type="info" size="small">
        自动激活PromptX角色并执行认知循环
      </el-tag>
    </el-form-item>

    <!-- 条件显示:PromptX角色选择 -->
    <template v-if="form.agentType === 'promptx'">
      <PromptXRoleSelector
        v-model="form.promptxRoleId"
        @role-selected="handleRoleSelected"
      />
    </template>

    <!-- 系统提示词 -->
    <el-form-item label="系统提示词" prop="systemPrompt">
      <el-input
        type="textarea"
        :rows="10"
        v-model="form.systemPrompt"
        :readonly="form.agentType === 'promptx'"
        placeholder="系统提示词内容">
      </el-input>
      <el-alert
        v-if="form.agentType === 'promptx'"
        type="info"
        :closable="false"
        show-icon>
        PromptX智能体的系统提示词由标准模板生成,确保认知循环正确执行
      </el-alert>
    </el-form-item>

    <!-- 其他现有字段... -->
  </el-form>
</template>

<script>
import PromptXRoleSelector from '@/components/PromptXRoleSelector.vue'

export default {
  components: {
    PromptXRoleSelector
  },
  data() {
    return {
      form: {
        agentType: 'normal',      // 默认类型
        promptxRoleId: '',
        promptxRoleSource: '',
        systemPrompt: '',
        // ... 其他字段
      }
    }
  },
  watch: {
    'form.agentType'(newVal) {
      if (newVal === 'normal') {
        // 切换回普通模式,清空PromptX字段
        this.form.promptxRoleId = ''
        this.form.promptxRoleSource = ''
        this.form.systemPrompt = ''
      }
    }
  },
  methods: {
    async handleRoleSelected(role) {
      // 角色选择后,自动生成系统提示词
      this.form.promptxRoleSource = role.source

      const res = await this.$api.generatePromptXSystemPrompt({
        roleId: role.id,
        roleName: role.name,
        roleDescription: role.description
      })

      this.form.systemPrompt = res.data
    }
  }
}
</script>
```

**PromptXRoleSelector组件**:

```vue
<template>
  <el-form-item label="选择PromptX角色" required>
    <el-select
      v-model="selectedRoleId"
      placeholder="请选择角色"
      filterable
      @change="handleRoleChange">

      <el-option-group label="📦 系统角色">
        <el-option
          v-for="role in systemRoles"
          :key="role.id"
          :label="role.name"
          :value="role.id">
          <div class="role-option">
            <span class="role-name">{{ role.name }}</span>
            <span class="role-id">({{ role.id }})</span>
            <p class="role-desc">{{ role.description }}</p>
          </div>
        </el-option>
      </el-option-group>

      <el-option-group label="👤 用户角色">
        <el-option
          v-for="role in userRoles"
          :key="role.id"
          :label="role.name"
          :value="role.id">
          <div class="role-option">
            <span class="role-name">{{ role.name }}</span>
            <span class="role-id">({{ role.id }})</span>
            <p class="role-desc">{{ role.description }}</p>
          </div>
        </el-option>
      </el-option-group>
    </el-select>

    <el-button
      icon="Refresh"
      @click="refreshRoles"
      :loading="loading"
      type="text">
      刷新角色列表
    </el-button>
  </el-form-item>
</template>

<script>
export default {
  props: {
    modelValue: String  // v-model绑定的角色ID
  },
  emits: ['update:modelValue', 'role-selected'],
  data() {
    return {
      selectedRoleId: '',
      systemRoles: [],
      userRoles: [],
      allRoles: [],
      loading: false
    }
  },
  mounted() {
    this.loadRoles()
  },
  methods: {
    async loadRoles() {
      this.loading = true
      try {
        const res = await this.$api.getPromptXRoles()
        this.allRoles = res.data

        // 按source分组
        this.systemRoles = res.data.filter(r => r.source === 'package')
        this.userRoles = res.data.filter(r => r.source === 'user')
      } catch (error) {
        this.$message.error('加载PromptX角色列表失败')
      } finally {
        this.loading = false
      }
    },
    async refreshRoles() {
      await this.loadRoles()
      this.$message.success('角色列表已刷新')
    },
    handleRoleChange(roleId) {
      const role = this.allRoles.find(r => r.id === roleId)
      this.$emit('update:modelValue', roleId)
      this.$emit('role-selected', role)
    }
  }
}
</script>

<style scoped>
.role-option {
  padding: 5px 0;
}
.role-name {
  font-weight: 600;
}
.role-id {
  color: #909399;
  font-size: 12px;
  margin-left: 8px;
}
.role-desc {
  color: #606266;
  font-size: 12px;
  margin: 4px 0 0 0;
}
</style>
```

### Element Plus组件选择

**使用的组件**:
- `el-radio-group` - 智能体类型选择
- `el-select` + `el-option-group` - 角色选择(支持分组)
- `el-input` textarea - 系统提示词显示
- `el-alert` - 提示信息
- `el-button` - 刷新按钮
- `el-tag` - 类型标识

**选择理由**:
- Element Plus是项目现有UI库
- 组件API稳定,文档完善
- 支持响应式布局和主题定制

---

## 5. LLM工具调用验证

### 决策: 通过系统提示词引导LLM执行工具调用

**验证方法**:

1. **LLM配置检查**:
```python
# 确认LLM支持function calling
def verify_llm_function_calling_support():
    """验证当前配置的LLM是否支持function calling"""
    llm_config = get_llm_config()

    # OpenAI, Claude, GLM-4等模型支持
    supported_models = ['gpt-', 'claude-', 'glm-4']

    if any(model in llm_config['model_name'] for model in supported_models):
        return True

    logger.warning(f"LLM {llm_config['model_name']} may not support function calling")
    return False
```

2. **系统提示词引导效果**:
```markdown
必须遵循的工作流程:
1. 对话开始时,使用 promptx_action 工具激活角色:{{ROLE_ID}}
2. 新任务时,先执行 promptx_recall(role, null) 进行DMN扫描
3. 根据网络图选择关键词,多轮 promptx_recall 深挖
4. 对话结束前,执行 promptx_remember 保存新知
```

3. **工具调用日志格式**:
```python
# 记录到专门的MCP工具调用日志
{
    "timestamp": "2025-12-02T10:30:00Z",
    "session_id": "session_123",
    "agent_id": "agent_promptx_001",
    "tool_name": "promptx_action",
    "arguments": {
        "role": "product-manager"
    },
    "result": {
        "success": true,
        "data": "角色激活成功..."
    },
    "duration_ms": 120
}
```

### 测试场景

**测试1: 角色激活验证**
```python
# 创建PromptX智能体,发起对话
# 预期: 第一轮对话LLM应调用promptx_action
assert "promptx_action" in mcp_call_logs[0]["tool_name"]
assert mcp_call_logs[0]["arguments"]["role"] == "product-manager"
```

**测试2: DMN扫描验证**
```python
# 用户提出需要专业知识的问题
# 预期: LLM应先执行recall(null)查看记忆网络
assert "promptx_recall" in mcp_call_logs[1]["tool_name"]
assert mcp_call_logs[1]["arguments"]["query"] is None  # DMN模式
```

**测试3: Remember验证**
```python
# 对话结束后检查
# 预期: 至少有一次remember调用
remember_calls = [log for log in mcp_call_logs if log["tool_name"] == "promptx_remember"]
assert len(remember_calls) >= 1
```

---

## 6. 技术选型总结

| 领域 | 决策 | 理由 |
|------|------|------|
| PromptX角色发现 | MCP discover工具 | 官方接口,自动聚合三层来源 |
| 系统提示词模板 | Markdown文件 + 字符串替换 | 简单高效,易维护 |
| 数据库扩展 | 添加3个字段到现有表 | 最小侵入,向后兼容 |
| 前端组件 | 修改roleConfig + 新增selector | 统一体验,复用逻辑 |
| UI库 | Element Plus | 项目现有技术栈 |
| 错误处理 | 三层机制(MCP/工具/前端) | 全面覆盖,优雅降级 |
| LLM验证 | 系统提示词引导 + 日志验证 | 无需修改LLM配置 |

---

## 7. 遗留问题和风险

### 已解决
- ✅ PromptX MCP服务连接方式确认
- ✅ 角色数据结构和来源标识明确
- ✅ 系统提示词模板设计完成
- ✅ 数据库扩展方案确定
- ✅ 前端UI集成方案设计

### 需在实施中验证
- ⚠️ PromptX MCP服务的实际性能(响应时间)
- ⚠️ 大量角色(50+)时的UI加载性能
- ⚠️ 系统提示词对不同LLM模型的引导效果

### 已知限制
- PromptX MCP服务必须在线,无离线模式
- 系统提示词为只读,用户无法自定义(设计如此)
- 依赖LLM支持function calling能力

---

**下一步**: 进入Phase 1,基于本研究结果设计详细的数据模型和API合约。
