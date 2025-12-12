"""
PromptX集成测试脚本
验证新的action驱动实现

测试内容：
1. MCP管理器初始化
2. PromptX服务可用性
3. 获取角色列表
4. 激活角色（action）
5. 提取角色定义文本

运行方法：
    cd main/xiaozhi-server
    python test_promptx_integration.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

async def test_promptx_integration():
    """测试PromptX集成"""
    print("=" * 70)
    print("PromptX集成测试 - Action驱动实现验证")
    print("=" * 70)

    try:
        # 1. 获取MCP管理器
        print("\n[1/5] 初始化MCP管理器...")
        try:
            from core.providers.tools.server_mcp.mcp_manager import get_mcp_manager
            mcp_manager = get_mcp_manager()
            if not mcp_manager:
                print("❌ MCP管理器未初始化")
                print("   提示：请确保mcp_server_settings.json配置正确")
                return False
            print("✅ MCP管理器初始化成功")
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False

        # 2. 创建PromptX服务
        print("\n[2/5] 创建PromptX服务...")
        try:
            from core.providers.tools.server_mcp.promptx_service import PromptXService
            promptx_service = PromptXService(mcp_manager)
            print("✅ PromptX服务创建成功")
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            return False

        # 3. 检查服务可用性
        print("\n[3/5] 检查PromptX服务可用性...")
        try:
            is_available = await promptx_service.is_promptx_available()
            if not is_available:
                print("❌ PromptX服务不可用")
                print("   提示：请检查PromptX服务是否正在运行（默认端口5203）")
                return False
            print("✅ PromptX服务可用")
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            return False

        # 4. 获取角色列表
        print("\n[4/5] 获取PromptX角色列表...")
        try:
            roles = await promptx_service.get_promptx_roles()
            print(f"✅ 发现 {len(roles)} 个角色:")

            # 按来源分组显示
            system_roles = [r for r in roles if r.get('source') == 'system']
            project_roles = [r for r in roles if r.get('source') == 'project']
            user_roles = [r for r in roles if r.get('source') == 'user']

            if system_roles:
                print(f"\n   📦 系统角色 ({len(system_roles)}个):")
                for role in system_roles[:3]:
                    print(f"      - {role['id']}: {role['name']}")
                if len(system_roles) > 3:
                    print(f"      ... 还有 {len(system_roles)-3} 个")

            if project_roles:
                print(f"\n   🏗️ 项目角色 ({len(project_roles)}个):")
                for role in project_roles[:3]:
                    print(f"      - {role['id']}: {role['name']}")

            if user_roles:
                print(f"\n   👤 用户角色 ({len(user_roles)}个):")
                for role in user_roles[:3]:
                    print(f"      - {role['id']}: {role['name']}")

            if not roles:
                print("⚠️  未发现任何角色")
                return False

        except Exception as e:
            print(f"❌ 获取角色列表失败: {e}")
            import traceback
            traceback.print_exc()
            return False

        # 5. 测试激活角色
        print("\n[5/5] 测试激活角色（action）...")
        if roles:
            test_role = roles[0]
            print(f"\n   测试角色: {test_role['name']} ({test_role['id']})")

            try:
                result = await promptx_service.activate_role(test_role['id'])

                # 提取文本内容
                text = ""
                if hasattr(result, 'content'):
                    content = result.content
                    if content and len(content) > 0:
                        first_content = content[0]
                        if hasattr(first_content, 'text'):
                            text = first_content.text
                        elif isinstance(first_content, dict):
                            text = first_content.get('text', '')
                elif isinstance(result, dict):
                    content = result.get("content", [])
                    if content and isinstance(content, list) and len(content) > 0:
                        text = content[0].get("text", "")

                if not text:
                    print("❌ action返回内容为空")
                    return False

                print(f"\n   ✅ 角色定义获取成功:")
                print(f"      - 内容长度: {len(text)} 字符")
                print(f"      - 预估Token: ~{len(text)//4}")
                print(f"\n   前200字符预览:")
                print(f"   {'-' * 66}")
                preview = text[:200].replace('\n', '\n   ')
                print(f"   {preview}...")
                print(f"   {'-' * 66}")

                # 检查是否包含关键信息
                has_role_info = "角色" in text or "role" in text.lower()
                has_tools = "recall" in text.lower() or "remember" in text.lower()

                print(f"\n   内容检查:")
                print(f"      - 包含角色信息: {'✅' if has_role_info else '❌'}")
                print(f"      - 包含工具说明: {'✅' if has_tools else '❌'}")

            except Exception as e:
                print(f"❌ 激活角色失败: {e}")
                import traceback
                traceback.print_exc()
                return False

        print("\n" + "=" * 70)
        print("✅ 所有测试通过！PromptX集成工作正常")
        print("=" * 70)
        print("\n下一步：")
        print("1. 在管理后台选择PromptX角色")
        print("2. WebSocket连接时会自动加载角色定义")
        print("3. 查看日志确认: '✅ PromptX角色已加载'")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n开始测试...")
    result = asyncio.run(test_promptx_integration())

    if result:
        print("\n🎉 测试成功！")
        sys.exit(0)
    else:
        print("\n💥 测试失败，请检查错误信息")
        sys.exit(1)
