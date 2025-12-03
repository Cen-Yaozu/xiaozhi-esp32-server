/**
 * PromptX智能体集成 - API接口模块
 * @module apis/module/promptx
 */

import { getServiceUrl } from '../api'
import RequestService from '../httpRequest'

export default {
  /**
   * 获取PromptX角色列表
   * @param {Function} callback - 回调函数 callback({ data, err })
   * @returns {void}
   * @example
   * promptx.getPromptXRoles(({ data, err }) => {
   *   if (data && data.code === 0) {
   *     console.log('角色列表:', data.data);
   *   }
   * });
   */
  getPromptXRoles(callback) {
    RequestService.sendRequest()
      .url(`${getServiceUrl()}/promptx/roles`)
      .method('GET')
      .success((res) => {
        RequestService.clearRequestTime()
        callback({ data: res })
      })
      .fail((err) => {
        callback({ err })
      })
      .networkFail(() => {
        RequestService.reAjaxFun(() => {
          this.getPromptXRoles(callback)
        })
      })
      .send()
  },

  /**
   * 生成PromptX系统提示词
   * @param {Object} request - 生成提示词请求对象
   * @param {string} request.roleId - 角色ID
   * @param {string} request.roleName - 角色名称
   * @param {string} request.roleDescription - 角色描述
   * @param {Function} callback - 回调函数
   * @returns {void}
   * @example
   * promptx.generateSystemPrompt({
   *   roleId: 'product-manager',
   *   roleName: '产品经理',
   *   roleDescription: '专业的产品设计专家'
   * }, ({ data, err }) => {
   *   if (data && data.code === 0) {
   *     console.log('生成的系统提示词:', data.data);
   *   }
   * });
   */
  generateSystemPrompt(request, callback) {
    RequestService.sendRequest()
      .url(`${getServiceUrl()}/promptx/generate-prompt`)
      .method('POST')
      .data(request)
      .success((res) => {
        RequestService.clearRequestTime()
        callback({ data: res })
      })
      .fail((err) => {
        callback({ err })
      })
      .networkFail(() => {
        RequestService.reAjaxFun(() => {
          this.generateSystemPrompt(request, callback)
        })
      })
      .send()
  }
}
