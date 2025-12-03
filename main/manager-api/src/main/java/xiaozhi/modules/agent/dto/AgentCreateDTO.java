package xiaozhi.modules.agent.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

/**
 * 智能体创建DTO
 * 专用于新增智能体，不包含id、agentCode和sort字段，这些字段由系统自动生成/设置默认值
 */
@Data
@Schema(description = "智能体创建对象")
public class AgentCreateDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @Schema(description = "智能体名称", example = "客服助手")
    @NotBlank(message = "智能体名称不能为空")
    private String agentName;

    @NotBlank(message = "智能体类型不能为空")
    @Pattern(regexp = "^(normal|promptx)$", message = "智能体类型必须是normal或promptx")
    @Schema(description = "智能体类型", required = true, allowableValues = {"normal", "promptx"}, defaultValue = "normal")
    private String agentType = "normal";

    @Schema(description = "PromptX角色ID (promptx类型必填)")
    private String promptxRoleId;

    @Schema(description = "PromptX角色来源 (promptx类型必填)")
    private String promptxRoleSource;

    @Schema(description = "系统提示词 (normal类型必填, promptx类型自动生成)")
    private String systemPrompt;

    /**
     * 验证PromptX智能体字段
     */
    public void validatePromptXFields() {
        if ("promptx".equals(agentType)) {
            if (promptxRoleId == null || promptxRoleId.trim().isEmpty()) {
                throw new IllegalArgumentException("PromptX智能体必须指定promptxRoleId");
            }
            if (promptxRoleSource == null || promptxRoleSource.trim().isEmpty()) {
                throw new IllegalArgumentException("PromptX智能体必须指定promptxRoleSource");
            }
        }
    }
}