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
        POST /api/promptx/generate-prompt
        生成PromptX系统提示词

        Request Body:
            {
              "roleId": "product-manager",
              "roleName": "产品经理",
              "roleDescription": "专业的产品设计和需求分析专家"
            }

        Returns:
            {
              "code": 0,
              "msg": "success",
              "data": "# 你是一个集成PromptX的AI智能体\\n\\n## 角色信息..."
            }
        """
        try:
            logger.bind(tag=TAG).info("收到生成系统提示词请求")

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

            # 验证必填参数
            role_id = body.get("roleId")
            role_name = body.get("roleName")
            role_description = body.get("roleDescription")

            if not role_id or not role_name or not role_description:
                return web.json_response(
                    {
                        "code": 400,
                        "msg": "缺少必填参数: roleId, roleName, roleDescription",
                        "data": None
                    },
                    status=400
                )

            # 生成系统提示词
            system_prompt = self.template_service.generate_system_prompt(
                role_id=role_id,
                role_name=role_name,
                role_description=role_description
            )

            logger.bind(tag=TAG).info(f"成功生成系统提示词，角色: {role_name}")

            return web.json_response(
                {
                    "code": 0,
                    "msg": "success",
                    "data": system_prompt
                }
            )

        except ValueError as e:
            logger.bind(tag=TAG).warning(f"参数验证失败: {e}")
            return web.json_response(
                {
                    "code": 400,
                    "msg": str(e),
                    "data": None
                },
                status=400
            )
        except Exception as e:
            logger.bind(tag=TAG).error(f"生成系统提示词失败: {e}", exc_info=True)
            return web.json_response(
                {
                    "code": 500,
                    "msg": f"生成系统提示词失败: {str(e)}",
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
