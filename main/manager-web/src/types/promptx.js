/**
 * PromptX智能体集成 - 类型定义
 * 使用JSDoc提供类型提示和文档
 */

/**
 * PromptX角色信息
 * @typedef {Object} PromptXRole
 * @property {string} id - 角色ID, 如: product-manager
 * @property {string} name - 显示名称
 * @property {string} description - 功能描述
 * @property {'system'|'project'|'user'} source - 来源
 * @property {string} protocol - 资源类型, 固定为 'role'
 * @property {string} [reference] - 资源引用路径
 */

/**
 * 智能体配置 (扩展)
 * @typedef {Object} AgentConfig
 * @property {string} [id] - 智能体ID
 * @property {string} agentName - 智能体名称
 * @property {'normal'|'promptx'} agentType - 智能体类型
 * @property {string} [promptxRoleId] - PromptX角色ID (仅promptx类型)
 * @property {'system'|'project'|'user'} [promptxRoleSource] - PromptX角色来源 (仅promptx类型)
 * @property {string} systemPrompt - 系统提示词
 * @property {string} [llmModelId] - LLM模型ID
 * @property {string} [asrModelId] - ASR模型ID
 * @property {string} [ttsModelId] - TTS模型ID
 */

/**
 * 生成系统提示词请求
 * @typedef {Object} GeneratePromptRequest
 * @property {string} roleId - 角色ID
 * @property {string} roleName - 角色名称
 * @property {string} roleDescription - 角色描述
 */

/**
 * 角色分组 (用于UI展示)
 * @typedef {Object} RoleGroup
 * @property {string} label - 分组标签, 如: "📦 系统角色"
 * @property {'system'|'project'|'user'} source - 来源类型
 * @property {PromptXRole[]} roles - 该组的角色列表
 */

export default {
  // 导出空对象,仅用于JSDoc类型定义
}
