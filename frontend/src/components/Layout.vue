<template>
  <div class="layout-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <el-icon size="28"><School /></el-icon>
          <span>英语学习助手</span>
        </div>
        
        <nav class="nav-menu" v-if="userStore.isLoggedIn">
          <el-menu
            mode="horizontal"
            :default-active="$route.name"
            router
            class="nav-menu"
          >
            <el-menu-item index="Dashboard">
              <el-icon><DataBoard /></el-icon>
              <span>学习中心</span>
            </el-menu-item>
            <el-menu-item index="Textbooks">
              <el-icon><Document /></el-icon>
              <span>我的教材</span>
            </el-menu-item>
            <el-menu-item index="Chat">
              <el-icon><ChatDotRound /></el-icon>
              <span>智能对话</span>
            </el-menu-item>
            <el-menu-item index="GenerateTest">
              <el-icon><EditPen /></el-icon>
              <span>开始测试</span>
            </el-menu-item>
            <el-menu-item index="Statistics">
              <el-icon><TrendCharts /></el-icon>
              <span>学习统计</span>
            </el-menu-item>
          </el-menu>
        </nav>
        
        <div class="header-right">
          <template v-if="userStore.isLoggedIn">
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="user-info">
                <el-avatar :size="36" :src="userStore.user?.avatar_url">
                  {{ userStore.user?.name?.charAt(0) }}
                </el-avatar>
                <span class="user-name">{{ userStore.user?.name }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" @click="$router.push('/login')">登录</el-button>
            <el-button @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </el-header>
    
    <!-- 主内容区 -->
    <el-main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
    
    <!-- 页脚 -->
    <el-footer class="footer">
      <p>英语学习助手 © 2026 | 基于AI的智能学习平台</p>
    </el-footer>
  </div>
</template>

<script setup>
import { useUserStore } from '@/store/user'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()

function handleCommand(command) {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      ElMessageBox.confirm(
        '确定要退出登录吗？',
        '退出确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        userStore.logout()
        router.push('/')
      }).catch(() => {})
      break
  }
}
</script>

<style scoped lang="scss">
.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-color);
  cursor: pointer;
  
  &:hover {
    opacity: 0.8;
  }
}

.nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
  border: none !important;
  
  :deep(.el-menu-item) {
    height: 60px;
    line-height: 60px;
    font-size: 15px;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  
  .user-name {
    font-size: 14px;
    color: var(--text-regular);
  }
}

.main-content {
  flex: 1;
  background: var(--bg-color);
  padding: 24px 0;
}

.footer {
  background: #fff;
  text-align: center;
  color: var(--text-secondary);
  font-size: 13px;
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 12px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .user-name {
    display: none;
  }
}
</style>
