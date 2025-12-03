"""
PromptX服务封装
提供PromptX MCP工具的高级封装接口
"""

import asyncio
from typing import List, Dict, Any, Optional
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class PromptXService:
    """PromptX服务封装类,提供角色发现和工具调用功能"""

    def __init__(self, mcp_manager):
        """
        初始化PromptX服务

        Args:
            mcp_manager: ServerMCPManager实例,用于执行MCP工具调用
        """
        self.mcp_manager = mcp_manager
        self._promptx_available = None  # 缓存PromptX服务可用性

    async def is_promptx_available(self) -> bool:
        """
        检查PromptX MCP服务是否可用

        Returns:
            bool: True表示PromptX服务可用,False表示不可用
        """
        if self._promptx_available is not None:
            return self._promptx_available

        try:
            # 检查promptx_discover工具是否存在
            self._promptx_available = self.mcp_manager.is_mcp_tool("promptx_discover")
            if not self._promptx_available:
                logger.bind(tag=TAG).warning("PromptX MCP服务不可用: 未找到promptx_discover工具")
            return self._promptx_available
        except Exception as e:
            logger.bind(tag=TAG).error(f"检查PromptX服务可用性失败: {e}")
            self._promptx_available = False
            return False

    async def get_promptx_roles(self) -> List[Dict[str, Any]]:
        """
        获取PromptX角色列表
        调用MCP discover工具获取所有可用角色

        Returns:
            List[Dict]: 角色列表,每个角色包含以下字段:
                - id (str): 角色ID,如 "product-manager"
                - name (str): 角色显示名称,如 "产品经理"
                - description (str): 角色功能描述
                - source (str): 角色来源,如 "system", "project", "user"
                - protocol (str): 资源协议,通常为 "role"
                - reference (str): 资源引用路径

        Raises:
            RuntimeError: PromptX服务不可用时抛出
            Exception: MCP工具调用失败时抛出
        """
        # 检查服务可用性
        if not await self.is_promptx_available():
            error_msg = "PromptX MCP服务不可用,无法获取角色列表"
            logger.bind(tag=TAG).error(error_msg)
            raise RuntimeError(error_msg)

        try:
            logger.bind(tag=TAG).info("调用promptx_discover工具获取角色列表")

            # 调用MCP discover工具,focus='roles'表示只获取角色
            result = await self.mcp_manager.execute_tool(
                "promptx_discover",
                {"focus": "roles"}
            )

            logger.bind(tag=TAG).debug(f"promptx_discover返回结果: {result}")

            # 解析MCP工具返回结果
            # MCP工具通常返回格式为: { "content": [...], "isError": false }
            if isinstance(result, dict):
                if result.get("isError"):
                    error_msg = result.get("content", [{}])[0].get("text", "Unknown error")
                    raise Exception(f"MCP工具调用失败: {error_msg}")

                content = result.get("content", [])
                if content and isinstance(content, list):
                    # 提取文本内容并解析
                    text_content = content[0].get("text", "")
                    roles = self._parse_discover_result(text_content)
                    logger.bind(tag=TAG).info(f"成功获取{len(roles)}个PromptX角色")
                    return roles

            logger.bind(tag=TAG).warning("promptx_discover返回结果格式不符合预期")
            return []

        except Exception as e:
            logger.bind(tag=TAG).error(f"获取PromptX角色列表失败: {e}")
            raise

    def _parse_discover_result(self, text_content: str) -> List[Dict[str, Any]]:
        """
        解析discover工具返回的文本内容

        Args:
            text_content: discover工具返回的文本内容

        Returns:
            List[Dict]: 解析后的角色列表
        """
        try:
            import json

            # discover工具通常返回JSON格式的文本
            # 需要从文本中提取JSON部分
            # 示例格式: "可用角色: {...json data...}"

            # 尝试直接解析为JSON
            try:
                data = json.loads(text_content)
                if isinstance(data, dict) and "roles" in data:
                    return data["roles"]
                elif isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass

            # 如果直接解析失败,尝试从文本中提取JSON
            # 查找```json...```代码块或直接的JSON对象
            import re

            # 匹配```json...```代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', text_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                if isinstance(data, dict) and "roles" in data:
                    return data["roles"]
                elif isinstance(data, list):
                    return data

            # 匹配直接的JSON对象或数组
            json_match = re.search(r'(\{.*\}|\[.*\])', text_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                if isinstance(data, dict) and "roles" in data:
                    return data["roles"]
                elif isinstance(data, list):
                    return data

            logger.bind(tag=TAG).warning(f"无法从文本中解析角色数据: {text_content[:200]}")
            return []

        except Exception as e:
            logger.bind(tag=TAG).error(f"解析discover结果失败: {e}")
            return []

    async def activate_role(self, role_id: str) -> Dict[str, Any]:
        """
        激活指定的PromptX角色
        调用MCP action工具激活角色并加载其配置

        Args:
            role_id (str): 要激活的角色ID,如 "product-manager"

        Returns:
            Dict: 激活结果,包含角色配置和记忆网络信息

        Raises:
            RuntimeError: PromptX服务不可用时抛出
            Exception: MCP工具调用失败时抛出
        """
        if not await self.is_promptx_available():
            error_msg = "PromptX MCP服务不可用,无法激活角色"
            logger.bind(tag=TAG).error(error_msg)
            raise RuntimeError(error_msg)

        try:
            logger.bind(tag=TAG).info(f"激活PromptX角色: {role_id}")

            result = await self.mcp_manager.execute_tool(
                "promptx_action",
                {"role": role_id}
            )

            logger.bind(tag=TAG).debug(f"promptx_action返回结果: {result}")
            return result

        except Exception as e:
            logger.bind(tag=TAG).error(f"激活PromptX角色失败: {e}")
            raise

    async def recall_memory(
        self,
        role_id: str,
        query: Optional[str] = None,
        mode: str = "balanced"
    ) -> Dict[str, Any]:
        """
        回忆角色记忆
        调用MCP recall工具检索相关记忆

        Args:
            role_id (str): 角色ID
            query (Optional[str]): 检索关键词,None表示DMN扫描全景
            mode (str): 认知激活模式,可选值: "creative", "balanced", "focused"

        Returns:
            Dict: 记忆检索结果

        Raises:
            RuntimeError: PromptX服务不可用时抛出
            Exception: MCP工具调用失败时抛出
        """
        if not await self.is_promptx_available():
            error_msg = "PromptX MCP服务不可用,无法回忆记忆"
            logger.bind(tag=TAG).error(error_msg)
            raise RuntimeError(error_msg)

        try:
            logger.bind(tag=TAG).info(f"回忆PromptX角色记忆: {role_id}, 查询: {query}")

            params = {
                "role": role_id,
                "mode": mode
            }

            # query为None表示DMN扫描
            if query is not None:
                params["query"] = query

            result = await self.mcp_manager.execute_tool(
                "promptx_recall",
                params
            )

            logger.bind(tag=TAG).debug(f"promptx_recall返回结果: {result}")
            return result

        except Exception as e:
            logger.bind(tag=TAG).error(f"回忆PromptX角色记忆失败: {e}")
            raise

    async def remember(
        self,
        role_id: str,
        engrams: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        保存新记忆
        调用MCP remember工具保存记忆痕迹

        Args:
            role_id (str): 角色ID
            engrams (List[Dict]): 记忆痕迹列表,每项包含:
                - content (str): 记忆内容
                - schema (str): 概念序列,空格分隔
                - strength (float): 记忆强度 0-1
                - type (str): 记忆类型 "ATOMIC"|"LINK"|"PATTERN"

        Returns:
            Dict: 保存结果

        Raises:
            RuntimeError: PromptX服务不可用时抛出
            Exception: MCP工具调用失败时抛出
        """
        if not await self.is_promptx_available():
            error_msg = "PromptX MCP服务不可用,无法保存记忆"
            logger.bind(tag=TAG).error(error_msg)
            raise RuntimeError(error_msg)

        try:
            logger.bind(tag=TAG).info(f"保存PromptX角色记忆: {role_id}, {len(engrams)}条记忆")

            result = await self.mcp_manager.execute_tool(
                "promptx_remember",
                {
                    "role": role_id,
                    "engrams": engrams
                }
            )

            logger.bind(tag=TAG).debug(f"promptx_remember返回结果: {result}")
            return result

        except Exception as e:
            logger.bind(tag=TAG).error(f"保存PromptX角色记忆失败: {e}")
            raise
