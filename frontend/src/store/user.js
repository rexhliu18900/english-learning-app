import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, getUserInfo } from '@/api/auth'
import { setToken, removeToken, getToken } from '@/utils'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(getToken())
  const loading = ref(false)
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isParent = computed(() => user.value?.user_type === 'parent')
  const isStudent = computed(() => user.value?.user_type === 'student')
  
  // 方法
  async function loginAction(email, password) {
    loading.value = true
    try {
      const response = await login(email, password)
      const { access_token, user: userData } = response
      
      token.value = access_token
      user.value = userData
      setToken(access_token)
      
      return { success: true }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }
  
  async function registerAction(userData) {
    loading.value = true
    try {
      const response = await register(userData)
      const { access_token, user: newUser } = response
      
      token.value = access_token
      user.value = newUser
      setToken(access_token)
      
      return { success: true }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }
  
  async function fetchUserInfo() {
    if (!token.value) return
    
    loading.value = true
    try {
      const response = await getUserInfo()
      user.value = response
    } catch (error) {
      console.error('获取用户信息失败:', error)
      logout()
    } finally {
      loading.value = false
    }
  }
  
  function logout() {
    token.value = null
    user.value = null
    removeToken()
  }
  
  // 初始化时获取用户信息
  if (token.value && !user.value) {
    fetchUserInfo()
  }
  
  return {
    user,
    token,
    loading,
    isLoggedIn,
    isParent,
    isStudent,
    loginAction,
    registerAction,
    fetchUserInfo,
    logout
  }
})
