import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginPage.vue'),
    meta: { requiresAuth: false, guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterPage.vue'),
    meta: { requiresAuth: false, guestOnly: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/textbooks',
    name: 'Textbooks',
    component: () => import('@/views/TextbooksPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/textbooks/:id',
    name: 'TextbookDetail',
    component: () => import('@/views/TextbookDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/ChatPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/test/generate',
    name: 'GenerateTest',
    component: () => import('@/views/GenerateTestPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/test/:id',
    name: 'TakeTest',
    component: () => import('@/views/TakeTestPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/test/:id/result',
    name: 'TestResult',
    component: () => import('@/views/TestResultPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/StatisticsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfilePage.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // 检查是否只允许游客访问（如登录页）
  if (to.meta.guestOnly && userStore.isLoggedIn) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})

export default router
