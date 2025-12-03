package xiaozhi.modules.agent.service;

import java.util.List;

import xiaozhi.modules.agent.dto.PromptXRoleDTO;

/**
 * PromptX服务接口
 * 负责与Python xiaozhi-server的PromptX HTTP API交互
 *
 * @author Claude
 * @version 1.0
 */
public interface PromptXService {
    /**
     * 获取PromptX角色列表
     *
     * @return 角色列表
     */
    List<PromptXRoleDTO> getPromptXRoles();

    /**
     * 生成PromptX系统提示词
     *
     * @param roleId 角色ID
     * @param roleName 角色名称
     * @param roleDescription 角色描述
     * @return 生成的系统提示词
     */
    String generateSystemPrompt(String roleId, String roleName, String roleDescription);

    /**
     * 检查PromptX服务是否可用
     *
     * @return 是否可用
     */
    boolean isPromptXAvailable();
}
