package xiaozhi.modules.agent.entity;

import java.util.Date;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@TableName("ai_agent")
@Schema(description = "智能体信息")
public class AgentEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "智能体唯一标识")
    private String id;

    @Schema(description = "所属用户ID")
    private Long userId;

    @Schema(description = "智能体编码")
    private String agentCode;

    @Schema(description = "智能体名称")
    private String agentName;

    @Schema(description = "语音识别模型标识")
    private String asrModelId;

    @Schema(description = "语音活动检测标识")
    private String vadModelId;

    @Schema(description = "大语言模型标识")
    private String llmModelId;

    @Schema(description = "VLLM模型标识")
    private String vllmModelId;

    @Schema(description = "语音合成模型标识")
    private String ttsModelId;

    @Schema(description = "音色标识")
    private String ttsVoiceId;

    @Schema(description = "记忆模型标识")
    private String memModelId;

    @Schema(description = "意图模型标识")
    private String intentModelId;

    @Schema(description = "聊天记录配置（0不记录 1仅记录文本 2记录文本和语音）")
    private Integer chatHistoryConf;

    @Schema(description = "角色设定参数")
    private String systemPrompt;

    @Schema(description = "智能体类型: normal(普通智能体) | promptx(PromptX智能体)")
    private String agentType = "normal";

    @Schema(description = "PromptX角色ID (仅promptx类型有效)")
    private String promptxRoleId;

    @Schema(description = "PromptX角色来源: system/project/user (仅promptx类型有效)")
    private String promptxRoleSource;

    @Schema(description = "总结记忆", example = "构建可生长的动态记忆网络，在有限空间内保留关键信息的同时，智能维护信息演变轨迹\n" +
            "根据对话记录，总结user的重要信息，以便在未来的对话中提供更个性化的服务", required = false)
    private String summaryMemory;

    @Schema(description = "语言编码")
    private String langCode;

    @Schema(description = "交互语种")
    private String language;

    @Schema(description = "排序")
    private Integer sort;

    @Schema(description = "创建者")
    private Long creator;

    @Schema(description = "创建时间")
    private Date createdAt;

    @Schema(description = "更新者")
    private Long updater;

    @Schema(description = "更新时间")
    private Date updatedAt;

    /**
     * 判断是否为PromptX智能体
     */
    public boolean isPromptXAgent() {
        return "promptx".equalsIgnoreCase(this.agentType);
    }

    /**
     * 验证PromptX智能体字段完整性
     * @throws IllegalStateException 如果字段不完整
     */
    public void validatePromptXFields() {
        if (isPromptXAgent()) {
            if (promptxRoleId == null || promptxRoleId.trim().isEmpty()) {
                throw new IllegalStateException("PromptX智能体必须指定角色ID");
            }
            if (promptxRoleSource == null || promptxRoleSource.trim().isEmpty()) {
                throw new IllegalStateException("PromptX智能体必须指定角色来源");
            }
        }
    }
}
