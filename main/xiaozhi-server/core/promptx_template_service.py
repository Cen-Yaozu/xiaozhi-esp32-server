"""
PromptX系统提示词模板生成服务
负责读取模板文件并根据角色信息生成最终的系统提示词
"""

import os
from typing import Dict, Any
from config.config_loader import get_project_dir
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class PromptXTemplateService:
    """PromptX系统提示词模板服务"""

    def __init__(self):
        """初始化模板服务"""
        self.template_path = None
        self._template_content = None
        self._load_template()

    def _load_template(self) -> None:
        """加载系统提示词模板文件"""
        try:
            # 尝试多个可能的模板路径
            possible_paths = [
                os.path.join(get_project_dir(), "config", "templates", "promptx_agent_system_prompt_template.md"),
                os.path.join(get_project_dir(), "config", "templates", "promptx_agent_system_prompt.md"),
                os.path.join(get_project_dir(), "core", "config", "templates", "promptx_agent_system_prompt_template.md"),
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    self.template_path = path
                    break

            if not self.template_path:
                raise FileNotFoundError(
                    f"PromptX系统提示词模板文件未找到。尝试的路径: {possible_paths}"
                )

            # 读取模板内容
            with open(self.template_path, "r", encoding="utf-8") as f:
                self._template_content = f.read()

            logger.bind(tag=TAG).info(f"成功加载PromptX系统提示词模板: {self.template_path}")

        except Exception as e:
            logger.bind(tag=TAG).error(f"加载PromptX系统提示词模板失败: {e}")
            # 如果模板加载失败,使用默认模板
            self._template_content = self._get_default_template()
            logger.bind(tag=TAG).warning("使用默认PromptX系统提示词模板")

    def _get_default_template(self) -> str:
        """
        获取默认模板内容
        当模板文件不存在或读取失败时使用

        Returns:
            str: 默认模板内容
        """
        return """# 你是一个集成PromptX的AI智能体

## 角色信息

**角色ID**: {{ROLE_ID}}
**角色名称**: {{ROLE_NAME}}
**角色描述**: {{ROLE_DESCRIPTION}}

## 必须遵循的工作流程

### 第1步:对话开始时激活角色
- 使用 `promptx_action` 工具激活角色:**{{ROLE_ID}}**

### 第2步:遵循PromptX认知循环

#### 2.1 DMN全景扫描(第一步必做)
promptx_recall(role: "{{ROLE_ID}}", query: null)

#### 2.2 多轮深入挖掘(不要一次就停)
promptx_recall(role: "{{ROLE_ID}}", query: "关键词")

#### 2.3 组织回答
- 结合recall获得的记忆 + 预训练知识

#### 2.4 保存新知(对话结束前必做)
promptx_remember(role: "{{ROLE_ID}}", engrams: [...])

## 重要提示

- 每次对话都要执行完整的认知循环
- DMN扫描是第一步,不要跳过
- 多轮recall深入挖掘,不要一次就停
- 记得在对话结束前remember保存新知识
"""

    def generate_system_prompt(
        self,
        role_id: str,
        role_name: str,
        role_description: str
    ) -> str:
        """
        生成PromptX智能体的系统提示词

        Args:
            role_id (str): PromptX角色ID,如 "product-manager"
            role_name (str): 角色显示名称,如 "产品经理"
            role_description (str): 角色功能描述

        Returns:
            str: 生成的系统提示词内容

        Example:
            >>> service = PromptXTemplateService()
            >>> prompt = service.generate_system_prompt(
            ...     role_id="product-manager",
            ...     role_name="产品经理",
            ...     role_description="专业的产品设计和需求分析专家"
            ... )
        """
        try:
            # 验证参数
            if not role_id or not role_name:
                raise ValueError("角色ID和名称是必填参数")

            # 如果描述为空，使用默认值
            if not role_description:
                role_description = "暂无描述"

            # 重新加载模板(支持热更新)
            if self.template_path and os.path.exists(self.template_path):
                with open(self.template_path, "r", encoding="utf-8") as f:
                    template = f.read()
            else:
                template = self._template_content

            # 替换变量
            system_prompt = template.replace("{{ROLE_ID}}", role_id)
            system_prompt = system_prompt.replace("{{ROLE_NAME}}", role_name)
            system_prompt = system_prompt.replace("{{ROLE_DESCRIPTION}}", role_description)

            logger.bind(tag=TAG).info(
                f"成功生成PromptX系统提示词,角色: {role_name} ({role_id})"
            )

            return system_prompt

        except Exception as e:
            logger.bind(tag=TAG).error(f"生成PromptX系统提示词失败: {e}")
            raise

    def reload_template(self) -> None:
        """
        重新加载模板文件
        用于支持模板热更新
        """
        try:
            self._load_template()
            logger.bind(tag=TAG).info("PromptX系统提示词模板已重新加载")
        except Exception as e:
            logger.bind(tag=TAG).error(f"重新加载PromptX系统提示词模板失败: {e}")
            raise

    def get_template_path(self) -> str:
        """
        获取当前使用的模板文件路径

        Returns:
            str: 模板文件路径,如果使用默认模板则返回"default"
        """
        return self.template_path if self.template_path else "default"


# 创建全局单例实例
_instance = None


def get_promptx_template_service() -> PromptXTemplateService:
    """
    获取PromptX模板服务的全局单例实例

    Returns:
        PromptXTemplateService: 模板服务实例
    """
    global _instance
    if _instance is None:
        _instance = PromptXTemplateService()
    return _instance
