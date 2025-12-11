package xiaozhi.modules.agent.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 生成PromptX系统提示词请求
 */
@Data
@Schema(description = "生成系统提示词请求")
public class GeneratePromptRequest {

    @NotBlank(message = "角色ID不能为空")
    @Schema(description = "PromptX角色ID", required = true, example = "product-manager")
    private String roleId;

    @NotBlank(message = "角色名称不能为空")
    @Schema(description = "角色显示名称", required = true, example = "产品经理")
    private String roleName;

    @Schema(description = "角色功能描述", required = false, example = "专业的产品设计专家")
    private String roleDescription;
}
