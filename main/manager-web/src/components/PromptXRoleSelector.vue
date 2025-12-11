<template>
  <div class="promptx-role-selector">
    <el-select
      v-model="selectedRoleId"
      filterable
      :placeholder="$t('roleConfig.pleaseSelectPromptXRole')"
      class="role-select"
      @change="handleRoleChange"
      :loading="loading"
    >
      <el-option
        v-for="role in roles"
        :key="role.id"
        :label="role.name"
        :value="role.id"
      >
        <div class="role-option">
          <span class="role-name">{{ role.name }}</span>
          <span class="role-source" :class="'source-' + role.source">
            {{ formatSource(role.source) }}
          </span>
        </div>
      </el-option>
    </el-select>

    <div v-if="selectedRole" class="role-description">
      <div class="description-label">角色描述：</div>
      <div class="description-content">{{ selectedRole.description }}</div>
    </div>

    <div v-if="error" class="error-message">
      <i class="el-icon-warning"></i>
      {{ error }}
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'PromptXRoleSelector',
  props: {
    value: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      selectedRoleId: this.value,
      error: null
    }
  },
  computed: {
    ...mapState('promptxAgent', ['roles', 'loading']),
    selectedRole() {
      if (!this.selectedRoleId) return null
      return this.roles.find(role => role.id === this.selectedRoleId)
    }
  },
  watch: {
    value(newVal) {
      this.selectedRoleId = newVal
    }
  },
  created() {
    this.loadRoles()
  },
  methods: {
    ...mapActions('promptxAgent', ['fetchRoles']),
    async loadRoles() {
      try {
        await this.fetchRoles(true)
        this.error = null
      } catch (err) {
        this.error = err.message || '加载PromptX角色列表失败'
        console.error('Failed to load PromptX roles:', err)
      }
    },
    handleRoleChange(roleId) {
      const role = this.roles.find(r => r.id === roleId)
      this.$emit('input', roleId)
      this.$emit('change', {
        roleId: roleId,
        roleName: role ? role.name : '',
        roleDescription: role ? role.description : '',
        roleSource: role ? role.source : ''
      })
    },
    formatSource(source) {
      const sourceMap = {
        'system': '系统',
        'project': '项目',
        'user': '用户'
      }
      return sourceMap[source] || source
    }
  }
}
</script>

<style scoped>
.promptx-role-selector {
  width: 100%;
}

.role-select {
  width: 100%;
}

.role-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-name {
  flex: 1;
  font-size: 14px;
}

.role-source {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 8px;
}

.source-system {
  background-color: #e1f3ff;
  color: #409eff;
}

.source-project {
  background-color: #f0f9ff;
  color: #67c23a;
}

.source-user {
  background-color: #fef0f0;
  color: #f56c6c;
}

.role-description {
  margin-top: 12px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.description-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
  font-weight: 500;
}

.description-content {
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
}

.error-message {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 4px;
  color: #f56c6c;
  font-size: 13px;
  display: flex;
  align-items: center;
}

.error-message i {
  margin-right: 6px;
}
</style>
