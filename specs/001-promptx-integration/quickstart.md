# Quick Start: PromptX智能体集成开发

**Feature**: PromptX智能体集成
**Target Audience**: 开发人员
**Estimated Time**: 30-60分钟

## 前置条件

### 1. 环境要求

**必需软件**:
- Python 3.10+
- Node.js 16+ 和 npm/yarn
- MySQL 8.0+
- Docker Desktop (可选,用于容器化部署)
- Git

**必需服务**:
- PromptX MCP服务运行在 `http://127.0.0.1:5203/mcp`

### 2. 验证PromptX MCP服务

```bash
# 方法1: 使用curl测试
curl -X POST http://127.0.0.1:5203/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# 预期响应: 包含 promptx_discover, promptx_action, promptx_recall, promptx_remember 等工具

# 方法2: 使用PromptX Desktop应用
# 打开应用,确认HTTP服务显示为"运行中"

# 方法3: 检查进程
lsof -i :5203
# 预期输出: 显示PromptX进程占用5203端口
```

### 3. 克隆项目

```bash
cd ~/Projects
git clone https://github.com/xinnan-tech/xiaozhi-esp32-server.git
cd xiaozhi-esp32-server

# 切换到功能分支
git checkout 001-promptx-integration
```

---

## 后端开发设置

### Step 1: 安装Python依赖

```bash
cd main/xiaozhi-server

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 验证MCP库
python -c "import mcp; print(mcp.__version__)"
# 预期输出: 1.22.0 或更高版本
```

### Step 2: 配置数据库

```bash
# 启动MySQL (Docker方式)
docker-compose -f docker-compose_all.yml up -d xiaozhi-esp32-server-db

# 或使用本地MySQL
mysql -u root -p

# 执行数据库迁移
cd main/xiaozhi-server
python scripts/migrate_database.py

# 验证表结构
mysql -u root -p xiaozhi_db -e "DESC ai_agent;"
# 应该看到 agent_type, promptx_role_id, promptx_role_source 三个新字段
```

### Step 3: 验证MCP配置

```bash
cd main/xiaozhi-server

# 检查MCP服务配置
cat data/mcp_server_settings.json

# 确认PromptX配置正确:
# {
#   "promptx": {
#     "url": "http://127.0.0.1:5203/mcp",
#     "transport": "streamable-http",
#     "des": "PromptX AI角色和工具管理器",
#     "link": "https://github.com/Deepractice/PromptX"
#   }
# }
```

### Step 4: 创建系统提示词模板

```bash
# 创建模板目录
mkdir -p main/xiaozhi-server/core/config/templates

# 复制模板文件
cp promptx_agent_system_prompt_template.md \
   main/xiaozhi-server/core/config/templates/promptx_agent_system_prompt.md

# 验证模板文件
head -20 main/xiaozhi-server/core/config/templates/promptx_agent_system_prompt.md
```

### Step 5: 运行后端服务

```bash
cd main/xiaozhi-server

# 方式1: 直接运行Python
python main.py

# 方式2: 使用Docker
docker-compose -f docker-compose_all.yml up xiaozhi-esp32-server

# 服务启动后,验证API可用性
curl http://localhost:8000/api/promptx/roles
```

---

## 前端开发设置

### Step 1: 安装Node.js依赖

```bash
cd main/manager-web

# 安装依赖
npm install
# 或
yarn install

# 验证Element Plus (应该已安装)
npm list element-plus
```

### Step 2: 配置API端点

```bash
# 检查环境配置
cat .env.development

# 确认API基础URL:
# VITE_API_BASE_URL=http://localhost:8000/api

# 如需修改,编辑文件:
vi .env.development
```

### Step 3: 运行前端开发服务器

```bash
cd main/manager-web

# 启动开发服务器
npm run dev
# 或
yarn dev

# 访问智控台
# 浏览器打开: http://localhost:8002

# 登录后进入"智能体配置"页面
```

---

## 功能验证

### 测试1: 获取PromptX角色列表

**API测试**:
```bash
curl -X GET "http://localhost:8000/api/promptx/roles" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 预期响应:
# {
#   "code": 200,
#   "message": "success",
#   "data": [
#     {
#       "id": "product-manager",
#       "name": "产品经理",
#       "description": "专业的产品设计和需求分析专家",
#       "source": "system",
#       "protocol": "role"
#     },
#     ...
#   ]
# }
```

**UI测试**:
1. 登录智控台
2. 进入"智能体配置"页面
3. 点击"创建新智能体"
4. 选择智能体类型为"PromptX智能体"
5. 观察角色下拉菜单是否正确加载

### 测试2: 生成系统提示词

**API测试**:
```bash
curl -X POST "http://localhost:8000/api/promptx/generate-prompt" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "roleId": "product-manager",
    "roleName": "产品经理",
    "roleDescription": "专业的产品设计专家"
  }'

# 预期响应: 返回完整的系统提示词Markdown文本
```

**UI测试**:
1. 在创建智能体表单中选择PromptX角色
2. 系统应自动填充"系统提示词"字段
3. 字段应为只读状态
4. 显示提示信息:"PromptX智能体的系统提示词由标准模板生成"

### 测试3: 创建PromptX智能体

**API测试**:
```bash
curl -X POST "http://localhost:8000/api/agents/promptx" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "agentName": "产品经理小智",
    "agentType": "promptx",
    "promptxRoleId": "product-manager",
    "promptxRoleSource": "system",
    "llmModelId": "glm-4.6",
    "asrModelId": "SenseVoiceSmall",
    "ttsModelId": "EdgeTTS",
    "ttsVoiceId": "zh-CN-XiaoxiaoNeural"
  }'

# 预期响应:
# {
#   "code": 201,
#   "message": "智能体创建成功",
#   "data": {
#     "id": "agent_xxx",
#     "agentName": "产品经理小智",
#     "agentType": "promptx",
#     "promptxRoleId": "product-manager",
#     ...
#   }
# }
```

**UI测试**:
1. 填写所有必填字段
2. 点击"保存"按钮
3. 观察是否成功创建并跳转到智能体列表
4. 在列表中确认新智能体显示"PromptX智能体"标识

### 测试4: 对话验证 (端到端)

1. 在智能体列表中选择刚创建的"产品经理小智"
2. 进入对话界面
3. 发送测试消息:"帮我设计一个用户登录功能"
4. 观察LLM回复

**验证MCP工具调用** (查看日志):
```bash
# 后端日志中应看到:
# [INFO] MCP Tool Call: promptx_action(role="product-manager")
# [INFO] MCP Tool Call: promptx_recall(role="product-manager", query=null)
# [INFO] MCP Tool Call: promptx_recall(role="product-manager", query="登录 认证")
# [INFO] MCP Tool Call: promptx_remember(...)
```

---

## 故障排查

### 问题1: PromptX服务连接失败

**症状**:
```
503 Service Unavailable
PromptX服务当前不可用
```

**解决方案**:
```bash
# 1. 检查PromptX服务是否运行
lsof -i :5203

# 2. 如未运行,启动PromptX Desktop应用
# 或使用命令行启动:
npx @promptx/mcp-server --transport http --port 5203

# 3. 验证服务可访问
curl http://127.0.0.1:5203/mcp

# 4. 重启xiaozhi-server
```

### 问题2: 角色列表为空

**症状**:
```json
{
  "code": 200,
  "message": "success",
  "data": []
}
```

**解决方案**:
```bash
# 1. 检查PromptX服务的discover工具
curl -X POST http://127.0.0.1:5203/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "promptx_discover",
      "arguments": {}
    }
  }'

# 2. 确认PromptX中有可用角色
# 使用PromptX Desktop查看角色列表

# 3. 检查后端日志中的MCP调用详情
tail -f main/xiaozhi-server/logs/mcp_calls.log
```

### 问题3: 系统提示词生成失败

**症状**:
```
404 Not Found
Template file not found
```

**解决方案**:
```bash
# 1. 确认模板文件存在
ls -l main/xiaozhi-server/core/config/templates/promptx_agent_system_prompt.md

# 2. 如不存在,复制模板文件
cp promptx_agent_system_prompt_template.md \
   main/xiaozhi-server/core/config/templates/promptx_agent_system_prompt.md

# 3. 验证文件权限
chmod 644 main/xiaozhi-server/core/config/templates/promptx_agent_system_prompt.md

# 4. 重启服务
```

### 问题4: 数据库字段不存在

**症状**:
```
Unknown column 'agent_type' in 'field list'
```

**解决方案**:
```bash
# 1. 执行数据库迁移
cd main/xiaozhi-server
python scripts/migrate_database.py

# 2. 手动执行SQL (如自动迁移失败)
mysql -u root -p xiaozhi_db < migrations/v1.0.0_add_promptx_support.sql

# 3. 验证字段已添加
mysql -u root -p xiaozhi_db -e "DESC ai_agent;"
```

### 问题5: 前端角色选择器不显示

**症状**: 选择"PromptX智能体"后,角色下拉菜单不出现

**解决方案**:
1. 打开浏览器开发者工具(F12)
2. 查看Console错误信息
3. 检查Network请求,确认`/api/promptx/roles`返回200
4. 检查Vue组件加载:
```bash
# 确认组件文件存在
ls -l main/manager-web/src/components/PromptXRoleSelector.vue
ls -l main/manager-web/src/api/promptx.js

# 检查组件是否正确注册
grep -r "PromptXRoleSelector" main/manager-web/src/views/
```

---

## 测试数据准备

### 创建测试角色 (使用PromptX)

如果系统角色不够用,可以创建用户自定义角色:

```bash
# 进入PromptX目录
cd ~/Desktop/PromptX

# 使用女娲创建角色
# 在Claude Code或Cursor中,对话:
# "激活女娲,帮我创建一个'测试工程师'角色"

# 或手动创建角色文件
mkdir -p ~/.promptx/resource/role/test-engineer
cat > ~/.promptx/resource/role/test-engineer/test-engineer.role.md <<'EOF'
# 测试工程师

## 角色定位
你是一个专业的软件测试工程师,精通各种测试方法和工具。

## 核心能力
- 测试用例设计
- 自动化测试
- 性能测试
- 安全测试

## 工作原则
- 质量第一
- 全面覆盖
- 持续改进
EOF

# 刷新PromptX资源注册
# 重启PromptX Desktop应用或执行:
pkill -f promptx-mcp-server
npx @promptx/mcp-server --transport http --port 5203
```

### 创建测试智能体

```bash
# 使用API创建多个测试智能体
for role in product-manager java-developer test-engineer; do
  curl -X POST "http://localhost:8000/api/agents/promptx" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -d "{
      \"agentName\": \"${role}智能体\",
      \"agentType\": \"promptx\",
      \"promptxRoleId\": \"$role\",
      \"promptxRoleSource\": \"system\",
      \"llmModelId\": \"glm-4.6\"
    }"
  echo ""
done
```

---

## 开发工作流

### 日常开发

```bash
# 1. 启动所有服务
cd ~/Projects/xiaozhi-esp32-server

# 终端1: 启动后端
cd main/xiaozhi-server
source venv/bin/activate
python main.py

# 终端2: 启动前端
cd main/manager-web
npm run dev

# 终端3: 监控日志
tail -f main/xiaozhi-server/logs/app.log
tail -f main/xiaozhi-server/logs/mcp_calls.log

# 2. 访问应用
open http://localhost:8002

# 3. 代码修改后
# 后端: 自动重载(如使用uvicorn --reload)
# 前端: 自动热更新
```

### 运行测试

```bash
# 后端单元测试
cd main/xiaozhi-server
pytest tests/unit/test_promptx_service.py -v

# 后端集成测试
pytest tests/integration/test_promptx_mcp_integration.py -v

# 前端组件测试
cd main/manager-web
npm run test:unit
```

### 代码提交

```bash
# 1. 检查修改
git status
git diff

# 2. 添加文件
git add main/xiaozhi-server/core/providers/tools/server_mcp/promptx_service.py
git add main/xiaozhi-server/api/routes/promptx_agent.py
git add main/manager-web/src/components/PromptXRoleSelector.vue

# 3. 提交
git commit -m "feat: 实现PromptX智能体集成基础功能

- 后端: 添加PromptX角色发现API
- 后端: 实现系统提示词生成逻辑
- 前端: 新增PromptX角色选择器组件
- 数据库: 扩展智能体表支持PromptX类型

Refs: #001-promptx-integration"

# 4. 推送
git push origin 001-promptx-integration
```

---

## 下一步

完成开发环境搭建和基础验证后:

1. 阅读 [data-model.md](data-model.md) 了解完整的数据模型设计
2. 阅读 [contracts/promptx-agent-api.yaml](contracts/promptx-agent-api.yaml) 了解API规范
3. 执行 `/speckit.tasks` 生成详细的实施任务清单
4. 按照任务清单逐步实现功能

## 参考资源

- [PromptX官方文档](https://github.com/Deepractice/PromptX)
- [MCP协议规范](https://spec.modelcontextprotocol.io/)
- [小智ESP32服务器文档](https://github.com/xinnan-tech/xiaozhi-esp32-server)
- [Element Plus组件库](https://element-plus.org/)
- [FastAPI文档](https://fastapi.tiangolo.com/)

## 获取帮助

- 项目Issues: https://github.com/xinnan-tech/xiaozhi-esp32-server/issues
- 开发团队联系方式: (待补充)
- PromptX社区: https://github.com/Deepractice/PromptX/discussions
