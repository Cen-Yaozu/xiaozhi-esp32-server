package xiaozhi.modules.agent.controller;

import java.util.List;

import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.agent.dto.GeneratePromptRequest;
import xiaozhi.modules.agent.dto.PromptXRoleDTO;
import xiaozhi.modules.agent.service.PromptXService;

/**
 * PromptX角色和系统提示词管理
 *
 * @author Claude
 * @version 1.0
 */
@Tag(name = "PromptX管理")
@AllArgsConstructor
@RestController
@RequestMapping("/promptx")
public class PromptXController {
    private final PromptXService promptxService;

    @GetMapping("/roles")
    @Operation(summary = "获取PromptX角色列表")
    @RequiresPermissions("sys:role:normal")
    public Result<List<PromptXRoleDTO>> getRoles() {
        List<PromptXRoleDTO> roles = promptxService.getPromptXRoles();
        return new Result<List<PromptXRoleDTO>>().ok(roles);
    }

    @PostMapping("/generate-prompt")
    @Operation(summary = "生成PromptX系统提示词")
    @RequiresPermissions("sys:role:normal")
    public Result<String> generatePrompt(@RequestBody @Valid GeneratePromptRequest request) {
        String systemPrompt = promptxService.generateSystemPrompt(
            request.getRoleId(),
            request.getRoleName(),
            request.getRoleDescription()
        );
        return new Result<String>().ok(systemPrompt);
    }

    @GetMapping("/status")
    @Operation(summary = "检查PromptX服务状态")
    @RequiresPermissions("sys:role:normal")
    public Result<Boolean> checkStatus() {
        boolean available = promptxService.isPromptXAvailable();
        return new Result<Boolean>().ok(available);
    }
}
