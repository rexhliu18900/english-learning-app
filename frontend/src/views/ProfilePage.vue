<template>
  <div class="profile-page">
    <!-- 用户信息头部 -->
    <div class="profile-header">
      <div class="user-avatar">
        <img :src="user.avatar || defaultAvatar" alt="用户头像" />
        <button class="change-avatar-btn" @click="showAvatarPicker">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
            <circle cx="12" cy="13" r="4"></circle>
          </svg>
        </button>
      </div>
      <div class="user-info">
        <h2>{{ user.name }}</h2>
        <span class="user-role">{{ user.role === 'parent' ? '家长' : '学生' }}</span>
        <p class="user-email">{{ user.email }}</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <h3>学习概况</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-value">{{ userStats.totalTests }}</span>
          <span class="stat-label">测试次数</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ userStats.totalQuestions }}</span>
          <span class="stat-label">答题数量</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ userStats.avgScore }}%</span>
          <span class="stat-label">平均正确率</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ userStats.learningDays }}</span>
          <span class="stat-label">学习天数</span>
        </div>
      </div>
    </div>

    <!-- 设置菜单 -->
    <div class="settings-section">
      <h3>账号设置</h3>
      <div class="settings-list">
        <div class="setting-item" @click="editProfile">
          <div class="setting-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <div class="setting-info">
            <span class="setting-name">个人信息</span>
            <span class="setting-desc">修改昵称、头像等</span>
          </div>
          <span class="setting-arrow">›</span>
        </div>

        <div class="setting-item" @click="changePassword">
          <div class="setting-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
          </div>
          <div class="setting-info">
            <span class="setting-name">修改密码</span>
            <span class="setting-desc">定期修改保护账号安全</span>
          </div>
          <span class="setting-arrow">›</span>
        </div>

        <div class="setting-item" @click="openNotificationSettings">
          <div class="setting-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
          </div>
          <div class="setting-info">
            <span class="setting-name">消息通知</span>
            <span class="setting-desc">接收学习提醒和通知</span>
          </div>
          <el-switch v-model="settings.notification" class="setting-switch" />
        </div>

        <div class="setting-item" @click="openPrivacySettings">
          <div class="setting-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
          <div class="setting-info">
            <span class="setting-name">隐私设置</span>
            <span class="setting-desc">管理数据共享和隐私</span>
          </div>
          <span class="setting-arrow">›</span>
        </div>
      </div>
    </div>

    <!-- 学习设置 -->
    <div class="settings-section">
      <h3>学习设置</h3>
      <div class="settings-list">
        <div class="setting-item">
          <div class="setting-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="setting-info">
            <span class="setting-name">每日学习目标</span>
            <span class="setting-desc">当前: {{ settings.dailyGoal }}题/天</span>
          </div>
          <el-input-number v-model="settings.dailyGoal" :min="5" :max="50" size="small" />
        </div>

        <div class="setting-item">
          <div class="setting-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
            </svg>
          </div>
          <div class="setting-info">
            <span class="setting-name">默认难度</span>
            <span class="setting-desc">生成测试的默认难度</span>
          </div>
          <el-select v-model="settings.defaultDifficulty" size="small" style="width: 100px">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </div>

        <div class="setting-item">
          <div class="setting-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <div class="setting-info">
            <span class="setting-name">音效提示</span>
            <span class="setting-desc">答题正确/错误时的音效</span>
          </div>
          <el-switch v-model="settings.soundEffects" class="setting-switch" />
        </div>
      </div>
    </div>

    <!-- 关于 -->
    <div class="settings-section">
      <h3>关于</h3>
      <div class="settings-list">
        <div class="setting-item" @click="checkUpdate">
          <div class="setting-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
          </div>
          <div class="setting-info">
            <span class="setting-name">检查更新</span>
            <span class="setting-desc">当前版本 v1.0.0</span>
          </div>
          <span class="setting-arrow">›</span>
        </div>

        <div class="setting-item" @click="openHelp">
          <div class="setting-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </div>
          <div class="setting-info">
            <span class="setting-name">帮助中心</span>
            <span class="setting-desc">使用帮助和常见问题</span>
          </div>
          <span class="setting-arrow">›</span>
        </div>

        <div class="setting-item" @click="openAbout">
          <div class="setting-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
          </div>
          <div class="setting-info">
            <span class="setting-name">关于我们</span>
            <span class="setting-desc">了解产品更多信息</span>
          </div>
          <span class="setting-arrow">›</span>
        </div>
      </div>
    </div>

    <!-- 退出登录 -->
    <div class="logout-section">
      <button class="logout-btn" @click="handleLogout">
        退出登录
      </button>
    </div>

    <!-- 编辑个人信息对话框 -->
    <el-dialog v-model="showEditProfile" title="编辑个人信息" width="90%">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="昵称">
          <el-input v-model="editForm.name" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditProfile = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showChangePassword" title="修改密码" width="90%">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入当前密码" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showChangePassword = false">取消</el-button>
        <el-button type="primary" @click="savePassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const user = ref({
  name: userStore.user?.name || '小明',
  email: userStore.user?.email || 'xiaoming@example.com',
  role: userStore.user?.role || 'student',
  avatar: null
})

const userStats = ref({
  totalTests: 24,
  totalQuestions: 480,
  avgScore: 78,
  learningDays: 15
})

const settings = ref({
  notification: true,
  dailyGoal: 20,
  defaultDifficulty: 'medium',
  soundEffects: true
})

const showEditProfile = ref(false)
const showChangePassword = ref(false)

const editForm = reactive({
  name: '',
  phone: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

function showAvatarPicker() {
  ElMessage.info('头像上传功能开发中')
}

function editProfile() {
  editForm.name = user.value.name
  showEditProfile.value = true
}

function saveProfile() {
  if (!editForm.name.trim()) {
    ElMessage.warning('请输入昵称')
    return
  }
  user.value.name = editForm.name
  showEditProfile.value = false
  ElMessage.success('保存成功')
}

function changePassword() {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  showChangePassword.value = true
}

function savePassword() {
  if (!passwordForm.oldPassword) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!passwordForm.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  if (passwordForm.newPassword.length < 6) {
    ElMessage.warning('密码长度不能少于6位')
    return
  }
  
  // 调用API修改密码
  showChangePassword.value = false
  ElMessage.success('密码修改成功')
}

function openNotificationSettings() {
  ElMessage.info('消息通知设置')
}

function openPrivacySettings() {
  ElMessage.info('隐私设置')
}

function checkUpdate() {
  ElMessage.info('当前已是最新版本')
}

function openHelp() {
  ElMessage.info('帮助中心')
}

function openAbout() {
  ElMessageBox.alert('AI英语学习助手 v1.0.0\n\n一款专为初中生设计的智能英语学习应用', '关于我们', {
    confirmButtonText: '确定'
  })
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    userStore.logout()
    router.push({ name: 'Login' })
    ElMessage.success('已退出登录')
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100%;
  background: #f5f7fa;
  padding-bottom: 40px;
}

.profile-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  color: #fff;
}

.user-avatar {
  position: relative;
}

.user-avatar img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.change-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.change-avatar-btn svg {
  width: 14px;
  height: 14px;
  color: #667eea;
}

.user-info h2 {
  margin: 0 0 8px;
  font-size: 22px;
}

.user-role {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 12px;
  margin-bottom: 8px;
}

.user-email {
  margin: 0;
  opacity: 0.8;
  font-size: 14px;
}

.stats-section {
  margin: 20px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
}

.stats-section h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.settings-section {
  margin: 0 20px 20px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
}

.settings-section h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #333;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.setting-item {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item:hover {
  background: #fafafa;
  margin: 0 -20px;
  padding-left: 20px;
  padding-right: 20px;
}

.setting-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #f0f5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.setting-icon svg {
  width: 20px;
  height: 20px;
  color: #667eea;
}

.setting-info {
  flex: 1;
}

.setting-name {
  display: block;
  font-size: 15px;
  color: #333;
  margin-bottom: 4px;
}

.setting-desc {
  font-size: 12px;
  color: #999;
}

.setting-arrow {
  font-size: 20px;
  color: #ccc;
}

.setting-switch {
  flex-shrink: 0;
}

.logout-section {
  margin: 20px;
}

.logout-btn {
  width: 100%;
  padding: 16px;
  background: #fff;
  border: 1px solid #f56c6c;
  border-radius: 8px;
  color: #f56c6c;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #f56c6c;
  color: #fff;
}

@media (max-width: 480px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
