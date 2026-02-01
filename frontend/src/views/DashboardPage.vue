<template>
  <Layout>
    <div class="dashboard-page">
      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <div class="welcome-content">
          <h1>你好，{{ userStore.user?.name }}！</h1>
          <p>今天也要继续努力学习英语哦~</p>
        </div>
        <div class="quick-actions">
          <el-button type="primary" size="large" @click="$router.push('/test/generate')">
            <el-icon><EditPen /></el-icon>
            开始测试
          </el-button>
          <el-button size="large" @click="$router.push('/chat')">
            <el-icon><ChatDotRound /></el-icon>
            AI对话
          </el-button>
        </div>
      </div>
      
      <!-- 统计卡片 -->
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6">
            <div class="stat-card card">
              <div class="stat-value">{{ statistics.totalTests || 0 }}</div>
              <div class="stat-label">测试次数</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card card">
              <div class="stat-value">{{ statistics.totalQuestions || 0 }}</div>
              <div class="stat-label">完成题目</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card card">
              <div class="stat-value">{{ statistics.correctRate || 0 }}%</div>
              <div class="stat-label">正确率</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card card">
              <div class="stat-value">{{ textbooks.length }}</div>
              <div class="stat-label">教材数量</div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 功能入口 -->
      <div class="features-section">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="8">
            <div class="feature-card card" @click="$router.push('/textbooks')">
              <el-icon size="48" color="#409eff"><Document /></el-icon>
              <h3>我的教材</h3>
              <p>管理学习教材，查看知识点</p>
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="feature-card card" @click="$router.push('/chat')">
              <el-icon size="48" color="#67c23a"><ChatDotRound /></el-icon>
              <h3>智能对话</h3>
              <p>基于教材的AI问答助手</p>
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="feature-card card" @click="$router.push('/statistics')">
              <el-icon size="48" color="#e6a23c"><TrendCharts /></el-icon>
              <h3>学习统计</h3>
              <p>查看学习进度和成绩分析</p>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 最近测试 -->
      <div class="recent-section card">
        <div class="section-header">
          <h2>最近测试</h2>
          <el-button text type="primary" @click="$router.push('/test/records')">
            查看全部
          </el-button>
        </div>
        <div class="test-list" v-if="recentTests.length > 0">
          <div class="test-item" v-for="test in recentTests" :key="test.id">
            <div class="test-info">
              <span class="test-scope">{{ test.test_scope?.textbook_name || '综合测试' }}</span>
              <span class="test-date">{{ formatDate(test.completed_at || test.started_at) }}</span>
            </div>
            <div class="test-score">
              <el-tag :type="test.score >= 60 ? 'success' : 'danger'">
                {{ test.score.toFixed(1) }}%
              </el-tag>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无测试记录" />
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/store/user'
import { getStatistics, getTestRecords } from '@/api/tests'
import { getTextbooks } from '@/api/textbooks'
import { formatDate } from '@/utils'

const userStore = useUserStore()

const statistics = ref({})
const recentTests = ref([])
const textbooks = ref([])

onMounted(async () => {
  await loadData()
})

async function loadData() {
  try {
    const [statsRes, testsRes, booksRes] = await Promise.all([
      getStatistics(),
      getTestRecords(1, 5),
      getTextbooks()
    ])
    
    statistics.value = {
      totalTests: statsRes.total_tests || 0,
      totalQuestions: statsRes.total_questions || 0,
      correctRate: statsRes.correct_rate || 0
    }
    
    recentTests.value = testsRes || []
    textbooks.value = booksRes || []
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}
</script>

<style scoped lang="scss">
.dashboard-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.welcome-section {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 24px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-content h1 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 8px;
}

.welcome-content p {
  font-size: 16px;
  opacity: 0.9;
}

.quick-actions .el-button {
  margin-left: 12px;
}

.stats-section {
  margin-bottom: 24px;
  
  .stat-card {
    text-align: center;
    padding: 24px;
  }
  
  .stat-value {
    font-size: 36px;
    font-weight: 700;
    color: var(--primary-color);
    line-height: 1.2;
  }
  
  .stat-label {
    font-size: 14px;
    color: var(--text-secondary);
    margin-top: 8px;
  }
}

.features-section {
  margin-bottom: 24px;
  
  .feature-card {
    text-align: center;
    padding: 40px 24px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-5px);
    }
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      margin: 16px 0 8px;
      color: var(--text-primary);
    }
    
    p {
      font-size: 14px;
      color: var(--text-secondary);
    }
  }
}

.recent-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h2 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }
  
  .test-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    border-bottom: 1px solid var(--border-color);
    
    &:last-child {
      border-bottom: none;
    }
  }
  
  .test-info {
    .test-scope {
      font-size: 15px;
      color: var(--text-primary);
      margin-right: 12px;
    }
    
    .test-date {
      font-size: 13px;
      color: var(--text-secondary);
    }
  }
}

@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    text-align: center;
    gap: 24px;
  }
  
  .quick-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    .el-button {
      margin-left: 0;
    }
  }
}
</style>
