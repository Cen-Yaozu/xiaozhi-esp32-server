package xiaozhi.modules.agent.service.impl;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.exception.RenException;
import xiaozhi.modules.agent.dto.PromptXRoleDTO;
import xiaozhi.modules.agent.service.PromptXService;

/**
 * PromptX服务实现
 * 通过RestTemplate调用Python xiaozhi-server的HTTP API
 *
 * @author Claude
 * @version 1.0
 */
@Slf4j
@Service
@AllArgsConstructor
public class PromptXServiceImpl implements PromptXService {
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();

    // xiaozhi-server的HTTP端口，默认8003
    @Value("${xiaozhi.server.http-port:8003}")
    private int xiaozhiServerPort;

    @Value("${xiaozhi.server.host:127.0.0.1}")
    private String xiaozhiServerHost;

    /**
     * 获取xiaozhi-server基础URL
     */
    private String getBaseUrl() {
        return String.format("http://%s:%d", xiaozhiServerHost, xiaozhiServerPort);
    }

    @Override
    public List<PromptXRoleDTO> getPromptXRoles() {
        String url = getBaseUrl() + "/api/promptx/roles";
        log.info("调用Python API获取PromptX角色列表: {}", url);

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<String> entity = new HttpEntity<>(headers);

            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                entity,
                Map.class
            );

            Map<String, Object> responseBody = response.getBody();
            if (responseBody == null) {
                throw new RenException(ErrorCode.INTERNAL_SERVER_ERROR, "Python API返回空响应");
            }

            Integer code = (Integer) responseBody.get("code");
            if (code == null || code != 0) {
                String msg = (String) responseBody.get("msg");
                log.error("获取PromptX角色列表失败: {}", msg);
                throw new RenException(ErrorCode.INTERNAL_SERVER_ERROR, msg);
            }

            List<Map<String, Object>> dataList = (List<Map<String, Object>>) responseBody.get("data");
            if (dataList == null) {
                return new ArrayList<>();
            }

            // 转换为DTO
            List<PromptXRoleDTO> roles = new ArrayList<>();
            for (Map<String, Object> data : dataList) {
                PromptXRoleDTO role = new PromptXRoleDTO();
                role.setId((String) data.get("id"));
                role.setName((String) data.get("name"));
                role.setDescription((String) data.get("description"));
                role.setSource((String) data.get("source"));
                role.setProtocol((String) data.get("protocol"));
                role.setReference((String) data.get("reference"));
                roles.add(role);
            }

            log.info("成功获取{}个PromptX角色", roles.size());
            return roles;

        } catch (Exception e) {
            log.error("调用Python API获取角色列表失败", e);
            throw new RenException(ErrorCode.INTERNAL_SERVER_ERROR, "获取PromptX角色列表失败: " + e.getMessage());
        }
    }

    @Override
    public String generateSystemPrompt(String roleId, String roleName, String roleDescription) {
        if (StringUtils.isBlank(roleId) || StringUtils.isBlank(roleName) || StringUtils.isBlank(roleDescription)) {
            throw new RenException(ErrorCode.PARAMS_GET_ERROR, "roleId, roleName, roleDescription不能为空");
        }

        String url = getBaseUrl() + "/api/promptx/generate-prompt";
        log.info("调用Python API生成系统提示词: {}, roleId={}", url, roleId);

        try {
            // 构建请求体
            Map<String, String> requestBody = new HashMap<>();
            requestBody.put("roleId", roleId);
            requestBody.put("roleName", roleName);
            requestBody.put("roleDescription", roleDescription);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, String>> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                Map.class
            );

            Map<String, Object> responseBody = response.getBody();
            if (responseBody == null) {
                throw new RenException(ErrorCode.INTERNAL_SERVER_ERROR, "Python API返回空响应");
            }

            Integer code = (Integer) responseBody.get("code");
            if (code == null || code != 0) {
                String msg = (String) responseBody.get("msg");
                log.error("生成系统提示词失败: {}", msg);
                throw new RenException(ErrorCode.INTERNAL_SERVER_ERROR, msg);
            }

            String systemPrompt = (String) responseBody.get("data");
            if (StringUtils.isBlank(systemPrompt)) {
                throw new RenException(ErrorCode.INTERNAL_SERVER_ERROR, "Python API返回的系统提示词为空");
            }

            log.info("成功生成系统提示词，长度: {}", systemPrompt.length());
            return systemPrompt;

        } catch (Exception e) {
            log.error("调用Python API生成系统提示词失败", e);
            throw new RenException(ErrorCode.INTERNAL_SERVER_ERROR, "生成系统提示词失败: " + e.getMessage());
        }
    }

    @Override
    public boolean isPromptXAvailable() {
        try {
            // 尝试调用角色列表接口检查服务是否可用
            getPromptXRoles();
            return true;
        } catch (Exception e) {
            log.warn("PromptX服务不可用: {}", e.getMessage());
            return false;
        }
    }
}
