"""
PromptX HTTP API处理器
提供PromptX角色管理和系统提示词生成的HTTP接口
"""

import json
from aiohttp import web
from config.logger import setup_logging
from core.promptx_template_service import get_promptx_template_service

TAG = __name__
logger = setup_logging()


class PromptXHandler:
    """PromptX HTTP API处理器"""

    def __init__(self, mcp_manager=None):
        """
        初始化PromptX处理器

        Args:
            mcp_manager: ServerMCPManager实例，用于调用MCP工具
        """
        self.mcp_manager = mcp_manager
        self.template_service = get_promptx_template_service()
        self._promptx_service = None

    def _get_promptx_service(self):
        """延迟加载PromptX服务"""
        if self._promptx_service is None and self.mcp_manager:
            from core.providers.tools.server_mcp.promptx_service import PromptXService
            self._promptx_service = PromptXService(self.mcp_manager)
        return self._promptx_service

    async def handle_get_roles(self, request: web.Request) -> web.Response:
        """
        GET /api/promptx/roles
        获取PromptX角色列表

        Returns:
            {
              "code": 0,
              "msg": "success",
              "data": [
                {
                  "id": "product-manager",
                  "name": "产品经理",
                  "description": "专业的产品设计和需求分析专家",
                  "source": "system",
                  "protocol": "role",
                  "reference": "@package://..."
                }
              ]
            }
        """
        try:
            logger.bind(tag=TAG).info("收到获取PromptX角色列表请求")

            promptx_service = self._get_promptx_service()
            if not promptx_service:
                return web.json_response(
                    {
                        "code": 500,
                        "msg": "PromptX服务未初始化，请检查MCP Manager配置",
                        "data": None
                    },
                    status=500
                )

            # 检查PromptX服务是否可用
            is_available = await promptx_service.is_promptx_available()
            if not is_available:
                return web.json_response(
                    {
                        "code": 503,
                        "msg": "PromptX MCP服务不可用，请检查服务配置",
                        "data": None
                    },
                    status=503
                )

            # 获取角色列表
            roles = await promptx_service.get_promptx_roles()

            logger.bind(tag=TAG).info(f"成功获取{len(roles)}个PromptX角色")

            return web.json_response(
                {
                    "code": 0,
                    "msg": "success",
                    "data": roles
                }
            )

        except Exception as e:
            logger.bind(tag=TAG).error(f"获取PromptX角色列表失败: {e}", exc_info=True)
            return web.json_response(
                {
                    "code": 500,
                    "msg": f"获取角色列表失败: {str(e)}",
                    "data": None
                },
                status=500
            )

    async def handle_generate_prompt(self, request: web.Request) -> web.Response:
        """
        ❌ 已废弃 (Deprecated since 2025-12-12)

        POST /api/promptx/generate-prompt
        生成PromptX系统提示词

        【废弃说明】
        此接口已废弃，不再需要生成系统提示词。
        新实现在运行时通过 promptx_action 工具直接获取角色定义。

        【新的实现方式】
        - 前端只需保存 promptxRoleId，systemPrompt留空
        - 运行时在connection.py中调用_get_promptx_role_definition()
        - 直接使用action返回的角色定义作为系统提示词

        【保留原因】
        - 向后兼容，避免前端调用报错
        - 建议前端更新后不再调用此接口

        【相关代码】
        - 新实现：connection.py::_get_promptx_role_definition()
        - 相关文档：specs/001-promptx-integration/agent-workflow-comparison.md
        """
        try:
            logger.bind(tag=TAG).warning("⚠️ 调用了已废弃的接口: POST /api/promptx/generate-prompt")

            # 解析请求体
            try:
                body = await request.json()
            except json.JSONDecodeError:
                return web.json_response(
                    {
                        "code": 400,
                        "msg": "请求体格式错误，需要JSON格式",
                        "data": None
                    },
                    status=400
                )

            role_id = body.get("roleId", "unknown")
            role_name = body.get("roleName", "未知角色")

            # 返回废弃提示信息
            deprecated_message = f"""【此接口已废弃】

角色: {role_name} ({role_id})

新的PromptX实现：
1. 系统提示词在运行时通过 promptx_action 工具自动加载
2. 前端配置时，systemPrompt字段留空即可
3. 不需要在配置阶段生成提示词

优势：
- 减少Token消耗（节省2000+ tokens）
- 简化流程，减少API调用
- LLM根据action返回的角色定义自己决定工具调用

建议：前端更新后不再调用此接口。
"""

            return web.json_response(
                {
                    "code": 0,
                    "msg": "success (deprecated)",
                    "data": deprecated_message
                }
            )

        except Exception as e:
            logger.bind(tag=TAG).error(f"处理废弃接口失败: {e}", exc_info=True)
            return web.json_response(
                {
                    "code": 500,
                    "msg": f"处理失败: {str(e)}",
                    "data": None
                },
                status=500
            )

    async def handle_options(self, request: web.Request) -> web.Response:
        """处理OPTIONS预检请求（CORS）"""
        return web.Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )
