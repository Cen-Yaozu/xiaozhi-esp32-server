package xiaozhi.modules.agent.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * PromptX角色数据传输对象
 * 用于前后端传递角色信息
 */
@Data
@Schema(description = "PromptX角色信息")
public class PromptXRoleDTO {

    @Schema(description = "角色唯一标识", example = "product-manager")
    private String id;

    @Schema(description = "角色显示名称", example = "产品经理")
    private String name;

    @Schema(description = "角色功能描述", example = "专业的产品设计和需求分析专家")
    private String description;

    @Schema(description = "角色来源", example = "system", allowableValues = {"system", "project", "user"})
    private String source;

    @Schema(description = "资源协议/类型", example = "role")
    private String protocol;

    @Schema(description = "资源引用路径", example = "@package://resource/role/product-manager/product-manager.role.md")
    private String reference;
}
