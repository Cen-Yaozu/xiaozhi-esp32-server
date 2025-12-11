/**
 * PromptX智能体集成 - Vuex Store模块
 * @module store/modules/promptxAgent
 */

import Api from '../../apis/api'

const state = {
  /** @type {import('../../types/promptx').PromptXRole[]} */
  roles: [],

  /** @type {import('../../types/promptx').RoleGroup[]} */
  roleGroups: [],

  /** @type {boolean} */
  loading: false,

  /** @type {string|null} */
  error: null,

  /** @type {number|null} */
  lastFetchTime: null
}

const getters = {
  /**
   * 获取系统级角色
   * @param {Object} state
   * @returns {import('../../types/promptx').PromptXRole[]}
   */
  systemRoles: (state) => {
    return state.roles.filter(r => r.source === 'system')
  },

  /**
   * 获取项目级角色
   * @param {Object} state
   * @returns {import('../../types/promptx').PromptXRole[]}
   */
  projectRoles: (state) => {
    return state.roles.filter(r => r.source === 'project')
  },

  /**
   * 获取用户级角色
   * @param {Object} state
   * @returns {import('../../types/promptx').PromptXRole[]}
   */
  userRoles: (state) => {
    return state.roles.filter(r => r.source === 'user')
  },

  /**
   * 根据ID获取角色
   * @param {Object} state
   * @returns {Function}
   */
  getRoleById: (state) => (roleId) => {
    return state.roles.find(r => r.id === roleId)
  },

  /**
   * 是否需要刷新 (超过5分钟)
   * @param {Object} state
   * @returns {boolean}
   */
  needsRefresh: (state) => {
    if (!state.lastFetchTime) return true
    const CACHE_DURATION = 5 * 60 * 1000 // 5分钟
    return Date.now() - state.lastFetchTime > CACHE_DURATION
  }
}

const mutations = {
  /**
   * 设置角色列表
   * @param {Object} state
   * @param {import('../../types/promptx').PromptXRole[]} roles
   */
  SET_ROLES(state, roles) {
    state.roles = roles

    // 自动分组
    const groups = [
      {
        label: '📦 系统角色',
        source: 'system',
        roles: roles.filter(r => r.source === 'system')
      },
      {
        label: '🏢 项目角色',
        source: 'project',
        roles: roles.filter(r => r.source === 'project')
      },
      {
        label: '👤 用户角色',
        source: 'user',
        roles: roles.filter(r => r.source === 'user')
      }
    ]

    // 过滤空分组
    state.roleGroups = groups.filter(group => group.roles.length > 0)
  },

  /**
   * 设置加载状态
   * @param {Object} state
   * @param {boolean} loading
   */
  SET_LOADING(state, loading) {
    state.loading = loading
  },

  /**
   * 设置错误信息
   * @param {Object} state
   * @param {string|null} error
   */
  SET_ERROR(state, error) {
    state.error = error
  },

  /**
   * 设置最后获取时间
   * @param {Object} state
   * @param {number} time
   */
  SET_LAST_FETCH_TIME(state, time) {
    state.lastFetchTime = time
  }
}

const actions = {
  /**
   * 获取PromptX角色列表
   * @param {Object} context - Vuex上下文
   * @param {boolean} forceRefresh - 是否强制刷新
   * @returns {Promise<void>}
   */
  fetchRoles({ commit, getters }, forceRefresh = false) {
    return new Promise((resolve, reject) => {
      // 如果有缓存且不是强制刷新,直接返回
      if (!forceRefresh && !getters.needsRefresh) {
        resolve()
        return
      }

      commit('SET_LOADING', true)
      commit('SET_ERROR', null)

      Api.promptx.getPromptXRoles(({ data: res, err }) => {
        commit('SET_LOADING', false)

        if (err || !res) {
          const errorMsg = err?.message || '获取角色列表失败'
          commit('SET_ERROR', errorMsg)
          reject(new Error(errorMsg))
          return
        }

        // res.data 是响应体 { code: 0, msg: 'success', data: [...] }
        // res.data.data 才是真正的角色列表
        const responseBody = res.data || {}
        commit('SET_ROLES', responseBody.data || [])
        commit('SET_LAST_FETCH_TIME', Date.now())
        resolve()
      })
    })
  },

  /**
   * 生成系统提示词
   * @param {Object} context - Vuex上下文
   * @param {import('../../types/promptx').GeneratePromptRequest} request
   * @returns {Promise<string>}
   */
    generateSystemPrompt({ commit }, request) {
      return new Promise((resolve, reject) => {
        Api.promptx.generateSystemPrompt(request, ({ data, err }) => {
          const body = data?.data
          if (err || !body || body.code !== 0) {
            const errorMsg = err?.message || body?.msg || '生成系统提示词失败'
            reject(new Error(errorMsg))
            return
          }

          resolve(body.data)
        })
      })
    }
  }

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
