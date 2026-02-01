<template>
  <div class="statistics-page">
    <div class="page-header">
      <h2>学习统计</h2>
      <p class="subtitle">记录你的学习成长轨迹</p>
    </div>

    <!-- 概览卡片 -->
    <div class="overview-cards">
      <div class="overview-card">
        <div class="card-icon blue">
          <span>📝</span>
        </div>
        <div class="card-content">
          <span class="card-value">{{ stats.totalTests }}</span>
          <span class="card-label">累计测试</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon green">
          <span>✅</span>
        </div>
        <div class="card-content">
          <span class="card-value">{{ stats.totalCorrect }}</span>
          <span class="card-label">累计正确</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon purple">
          <span>🎯</span>
        </div>
        <div class="card-content">
          <span class="card-value">{{ stats.avgScore }}%</span>
          <span class="card-label">平均正确率</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon orange">
          <span>⏱</span>
        </div>
        <div class="card-content">
          <span class="card-value">{{ formatTime(stats.totalTime) }}</span>
          <span class="card-label">累计学习</span>
        </div>
      </div>
    </div>

    <!-- 正确率趋势图 -->
    <div class="chart-card">
      <h3>📈 正确率趋势</h3>
      <div class="chart-container">
        <canvas ref="trendChartRef"></canvas>
      </div>
    </div>

    <!-- 知识点掌握情况 -->
    <div class="knowledge-section">
      <h3>📚 知识点掌握情况</h3>
      <div class="knowledge-tabs">
        <button
          v-for="tab in knowledgeTabs"
          :key="tab.key"
          :class="['tab-btn', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
      <div class="knowledge-list">
        <div
          v-for="(item, index) in knowledgeStats"
          :key="index"
          class="knowledge-item"
        >
          <div class="knowledge-info">
            <span class="knowledge-name">{{ item.name }}</span>
            <span class="knowledge-count">{{ item.correct }}/{{ item.total }} 题</span>
          </div>
          <div class="knowledge-bar">
            <div
              class="bar-fill"
              :style="{ width: item.rate + '%', background: getRateColor(item.rate) }"
            ></div>
          </div>
          <span class="knowledge-rate">{{ item.rate }}%</span>
        </div>
      </div>
    </div>

    <!-- 薄弱知识点 -->
    <div class="weak-section">
      <h3>⚠️ 需要加强的知识点</h3>
      <div class="weak-list" v-if="weakPoints.length > 0">
        <div
          v-for="(item, index) in weakPoints"
          :key="index"
          class="weak-item"
          @click="practiceWeakPoint(item)"
        >
          <div class="weak-info">
            <span class="weak-name">{{ item.name }}</span>
            <span class="weak-rate">正确率 {{ item.rate }}%</span>
          </div>
          <button class="practice-btn">练习</button>
        </div>
      </div>
      <div class="empty-state" v-else>
        <span class="empty-icon">🎉</span>
        <p>太棒了！没有需要加强的知识点</p>
      </div>
    </div>

    <!-- 测试历史 -->
    <div class="history-section">
      <h3>📋 测试历史</h3>
      <div class="history-list">
        <div
          v-for="(test, index) in testHistory"
          :key="index"
          class="history-item"
        >
          <div class="history-info">
            <span class="history-title">{{ test.title }}</span>
            <span class="history-date">{{ test.date }}</span>
          </div>
          <div class="history-score">
            <span :class="['score-badge', getScoreClass(test.rate)]">
              {{ test.rate }}%
            </span>
            <span class="history-detail">{{ test.correct }}/{{ test.total }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Chart, registerables } from 'chart.js'
import { getStatistics } from '@/api/tests'

Chart.register(...registerables)

const router = useRouter()
const trendChartRef = ref(null)
const activeTab = ref('vocabulary')

const knowledgeTabs = [
  { key: 'vocabulary', label: '词汇' },
  { key: 'grammar', label: '语法' },
  { key: 'sentence', label: '句型' }
]

// 模拟数据
const stats = ref({
  totalTests: 24,
  totalCorrect: 186,
  avgScore: 78,
  totalTime: 7200
})

const knowledgeStats = ref([
  { name: '现在完成时', correct: 15, total: 20, rate: 75 },
  { name: '过去进行时', correct: 12, total: 15, rate: 80 },
  { name: 'since/for 区别', correct: 8, total: 12, rate: 67 },
  { name: '被动语态', correct: 10, total: 18, rate: 56 },
  { name: '情态动词', correct: 14, total: 16, rate: 88 },
  { name: '定语从句', correct: 6, total: 10, rate: 60 }
])

const weakPoints = ref([
  { name: '被动语态', rate: 56, id: 'passive_voice' },
  { name: '定语从句', rate: 60, id: 'relative_clause' },
  { name: 'since/for 区别', rate: 67, id: 'since_for' }
])

const testHistory = ref([
  { title: 'Unit 1-2 综合测试', date: '2025-01-15', correct: 8, total: 10, rate: 80 },
  { title: 'Unit 3 词汇测试', date: '2025-01-14', correct: 14, total: 15, rate: 93 },
  { title: 'Unit 1 语法测试', date: '2025-01-13', correct: 6, total: 10, rate: 60 },
  { title: '综合模拟测试', date: '2025-01-12', correct: 18, total: 25, rate: 72 }
])

onMounted(async () => {
  await loadStatistics()
  await nextTick()
  renderChart()
})

async function loadStatistics() {
  try {
    const response = await getStatistics()
    // 更新数据...
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}小时${mins}分`
  }
  return `${mins}分钟`
}

function getRateColor(rate) {
  if (rate >= 80) return '#52c41a'
  if (rate >= 60) return '#faad14'
  return '#f56c6c'
}

function getScoreClass(rate) {
  if (rate >= 90) return 'excellent'
  if (rate >= 80) return 'good'
  if (rate >= 60) return 'pass'
  return 'fail'
}

function renderChart() {
  if (!trendChartRef.value) return

  const ctx = trendChartRef.value.getContext('2d')
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['第1周', '第2周', '第3周', '第4周', '本周'],
      datasets: [{
        label: '正确率',
        data: [65, 68, 72, 75, 78],
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#667eea',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: {
            callback: (value) => value + '%'
          }
        }
      }
    }
  })
}

function practiceWeakPoint(item) {
  router.push({
    name: 'GenerateTest',
    query: { knowledge: item.id, focus: item.name }
  })
}
</script>

<style scoped>
.statistics-page {
  min-height: 100%;
  background: #f5f7fa;
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #333;
}

.subtitle {
  margin: 0;
  color: #999;
  font-size: 14px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.overview-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.card-icon.blue {
  background: #e6f7ff;
}

.card-icon.green {
  background: #f6ffed;
}

.card-icon.purple {
  background: #f9f0ff;
}

.card-icon.orange {
  background: #fff7e6;
}

.card-content {
  display: flex;
  flex-direction: column;
}

.card-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.card-label {
  font-size: 12px;
  color: #999;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.chart-card h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #333;
}

.chart-container {
  height: 200px;
}

.knowledge-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.knowledge-section h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #333;
}

.knowledge-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 8px 16px;
  border: none;
  background: #f0f0f0;
  border-radius: 16px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.knowledge-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.knowledge-info {
  width: 140px;
  flex-shrink: 0;
}

.knowledge-name {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 2px;
}

.knowledge-count {
  font-size: 12px;
  color: #999;
}

.knowledge-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.knowledge-rate {
  width: 50px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.weak-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.weak-section h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #333;
}

.weak-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.weak-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff1f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.weak-item:hover {
  background: #ffe7e7;
}

.weak-name {
  font-size: 14px;
  color: #333;
}

.weak-rate {
  font-size: 12px;
  color: #f56c6c;
  margin-top: 4px;
  display: block;
}

.practice-btn {
  padding: 6px 16px;
  background: #f56c6c;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 32px;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.empty-state p {
  margin: 0;
  color: #52c41a;
  font-size: 14px;
}

.history-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
}

.history-section h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #333;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.history-item:last-child {
  border-bottom: none;
}

.history-title {
  font-size: 14px;
  color: #333;
  display: block;
  margin-bottom: 4px;
}

.history-date {
  font-size: 12px;
  color: #999;
}

.history-score {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.score-badge.excellent {
  background: #f6ffed;
  color: #52c41a;
}

.score-badge.good {
  background: #e6f7ff;
  color: #1890ff;
}

.score-badge.pass {
  background: #fff7e6;
  color: #faad14;
}

.score-badge.fail {
  background: #fff1f0;
  color: #f56c6c;
}

.history-detail {
  font-size: 12px;
  color: #999;
}
</style>
