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
            # 检查discover工具是否存在（PromptX MCP工具名称为discover）
            self._promptx_available = self.mcp_manager.is_mcp_tool("discover")
            if not self._promptx_available:
                logger.bind(tag=TAG).warning("PromptX MCP服务不可用: 未找到discover工具")
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
            logger.bind(tag=TAG).info("调用discover工具获取角色列表")

            # 调用MCP discover工具,focus='roles'表示只获取角色
            result = await self.mcp_manager.execute_tool(
                "discover",
                {"focus": "roles"}
            )

            logger.bind(tag=TAG).info(f"discover返回结果: {result}")

            # 解析MCP工具返回结果
            # MCP工具返回格式可能是对象或dict
            text_content = ""
            
            # 处理对象类型的返回结果（如CallToolResult）
            if hasattr(result, 'content'):
                content = result.content
                if content and len(content) > 0:
                    first_content = content[0]
                    if hasattr(first_content, 'text'):
                        text_content = first_content.text
                    elif isinstance(first_content, dict):
                        text_content = first_content.get('text', '')
            # 处理dict类型的返回结果
            elif isinstance(result, dict):
                if result.get("isError"):
                    error_msg = result.get("content", [{}])[0].get("text", "Unknown error")
                    raise Exception(f"MCP工具调用失败: {error_msg}")
                content = result.get("content", [])
                if content and isinstance(content, list):
                    text_content = content[0].get("text", "")
            
            if text_content:
                roles = self._parse_discover_result(text_content)
                logger.bind(tag=TAG).info(f"成功获取{len(roles)}个PromptX角色")
                return roles

            logger.bind(tag=TAG).warning("discover返回结果格式不符合预期")
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
            import re

            roles = []

            # 尝试直接解析为JSON
            try:
                data = json.loads(text_content)
                if isinstance(data, dict) and "roles" in data:
                    return data["roles"]
                elif isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass

            # 解析Markdown格式的角色列表
            # 格式示例:
            # 📦 **系统角色** (6个)
            # - `assistant`: assistant → action("assistant")
            # - `luban`: 鲁班 - AI工具集成专家 → action("luban")
            
            # 匹配角色行: - `role_id`: role_name - description → action("role_id")
            # 或: - `role_id`: role_name → action("role_id")
            role_pattern = r'- `([^`]+)`: ([^→]+)→ action\("([^"]+)"\)'
            
            current_source = "system"
            for line in text_content.split('\n'):
                # 检测角色来源
                if '**系统角色**' in line:
                    current_source = "system"
                elif '**项目角色**' in line:
                    current_source = "project"
                elif '**用户角色**' in line:
                    current_source = "user"
                
                # 匹配角色行
                match = re.search(role_pattern, line)
                if match:
                    role_id = match.group(1).strip()
                    name_desc = match.group(2).strip()
                    
                    # 分离名称和描述
                    if ' - ' in name_desc:
                        parts = name_desc.split(' - ', 1)
                        role_name = parts[0].strip()
                        role_description = parts[1].strip() if len(parts) > 1 else ""
                    else:
                        role_name = name_desc.strip()
                        role_description = ""
                    
                    roles.append({
                        "id": role_id,
                        "name": role_name,
                        "description": role_description,
                        "source": current_source,
                        "protocol": "role",
                        "reference": f"@role://{role_id}"
                    })

            if roles:
                logger.bind(tag=TAG).info(f"从Markdown格式解析出{len(roles)}个角色")
                return roles

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
