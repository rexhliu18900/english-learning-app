<template>
  <div class="test-result-page">
    <!-- 成绩卡片 -->
    <div class="score-card">
      <div class="score-circle" :class="scoreClass">
        <span class="score-value">{{ score }}</span>
        <span class="score-total">/{{ totalScore }}</span>
      </div>
      <div class="score-info">
        <h2>{{ scoreText }}</h2>
        <p>正确率 {{ correctRate }}%</p>
      </div>
      <div class="score-stats">
        <div class="stat-item correct">
          <span class="stat-icon">✓</span>
          <span class="stat-value">{{ correctCount }}</span>
          <span class="stat-label">正确</span>
        </div>
        <div class="stat-item wrong">
          <span class="stat-icon">✗</span>
          <span class="stat-value">{{ wrongCount }}</span>
          <span class="stat-label">错误</span>
        </div>
        <div class="stat-item time">
          <span class="stat-icon">⏱</span>
          <span class="stat-value">{{ formatTime(timeSpent) }}</span>
          <span class="stat-label">用时</span>
        </div>
      </div>
    </div>

    <!-- 评级 -->
    <div class="grade-section">
      <div class="grade-badge" :class="gradeClass">
        <span class="grade-icon">{{ gradeIcon }}</span>
        <span class="grade-text">{{ gradeText }}</span>
      </div>
      <p class="grade-encouragement">{{ encouragement }}</p>
    </div>

    <!-- 错题分析 -->
    <div class="error-analysis" v-if="wrongQuestions.length > 0">
      <h3>📝 错题分析</h3>
      <div class="error-list">
        <div
          v-for="(item, index) in wrongQuestions"
          :key="index"
          class="error-item"
        >
          <div class="error-header">
            <span class="question-num">第 {{ item.index }} 题</span>
            <span class="question-type">{{ item.typeText }}</span>
          </div>
          <div class="error-content">
            <div class="question-display">
              <div class="question-text" v-html="item.question"></div>
              <div class="question-options" v-if="item.options">
                <div
                  v-for="(opt, idx) in item.options"
                  :key="idx"
                  :class="['option', {
                    correct: idx === item.correctAnswer,
                    wrong: idx === item.userAnswer && idx !== item.correctAnswer
                  }]"
                >
                  <span class="option-letter">{{ String.fromCharCode(65 + idx) }}</span>
                  <span v-html="opt"></span>
                </div>
              </div>
            </div>
            <div class="analysis-section">
              <div class="analysis-item">
                <span class="analysis-label">你的答案：</span>
                <span class="analysis-value user-answer">{{ item.userAnswerText }}</span>
              </div>
              <div class="analysis-item">
                <span class="analysis-label">正确答案：</span>
                <span class="analysis-value correct-answer">{{ item.correctAnswerText }}</span>
              </div>
              <div class="analysis-item explanation" v-if="item.explanation">
                <span class="analysis-label">解析：</span>
                <span class="analysis-value" v-html="item.explanation"></span>
              </div>
              <div class="knowledge-tag" v-if="item.knowledge_point">
                <span class="tag-icon">📚</span>
                <span>{{ item.knowledge_point }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <button class="btn btn-outline" @click="reviewAnswers">
        <span>📖</span> 重新查看
      </button>
      <button class="btn btn-primary" @click="generateWrongTest" v-if="wrongCount > 0">
        <span>🎯</span> 错题重练
      </button>
      <button class="btn btn-success" @click="goHome">
        <span>🏠</span> 返回首页
      </button>
    </div>

    <!-- 学习建议 -->
    <div class="suggestions" v-if="suggestions.length > 0">
      <h3>💡 学习建议</h3>
      <ul>
        <li v-for="(s, index) in suggestions" :key="index">
          {{ s }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { generateWrongTest as generateWrongTestApi } from '@/api/tests'

const router = useRouter()
const route = useRoute()

const correctCount = ref(Number(route.params.correctCount) || 0)
const totalCount = ref(Number(route.params.totalCount) || 0)
const score = ref(Number(route.params.score) || 0)
const totalScore = ref(Number(route.params.totalScore) || 100)
const timeSpent = ref(Number(route.params.timeSpent) || 0)

// 模拟错题详情（实际应从后端获取）
const wrongQuestions = ref([
  {
    index: 2,
    type: 'choice',
    typeText: '选择题',
    question: 'She has lived in Beijing ___ 2010.',
    options: ['since', 'for', 'in', 'at'],
    userAnswer: 1,
    correctAnswer: 0,
    userAnswerText: 'for',
    correctAnswerText: 'since',
    explanation: '<strong>since</strong> 用于表示时间点的开始，后面接具体的时间点或年份。<br><strong>for</strong> 用于表示一段时间的持续。',
    knowledge_point: 'since / for 区别'
  },
  {
    index: 4,
    type: 'choice',
    typeText: '选择题',
    question: '___ volume please? I can\'t hear clearly.',
    options: ['Can you turn up', 'Can you turn down', 'Could you turn up', 'Could you turn down'],
    userAnswer: 1,
    correctAnswer: 2,
    userAnswerText: 'Can you turn down',
    correctAnswerText: 'Could you turn up',
    explanation: '<strong>Could</strong> 比 <strong>Can</strong> 更礼貌。<br><strong>Turn up</strong> 表示"调大"，符合句意"我听不清，请把音量调大"。',
    knowledge_point: '情态动词'
  }
])

const wrongCount = computed(() => totalCount.value - correctCount.value)
const correctRate = computed(() => Math.round((correctCount.value / totalCount.value) * 100))

const scoreClass = computed(() => {
  const rate = correctRate.value
  if (rate >= 90) return 'excellent'
  if (rate >= 80) return 'good'
  if (rate >= 60) return 'pass'
  return 'fail'
})

const scoreText = computed(() => {
  const rate = correctRate.value
  if (rate >= 90) return '太棒了！'
  if (rate >= 80) return '表现优秀！'
  if (rate >= 60) return '继续加油！'
  return '需要多练习！'
})

const gradeClass = computed(() => {
  const rate = correctRate.value
  if (rate >= 90) return 's'
  if (rate >= 80) return 'a'
  if (rate >= 70) return 'b'
  if (rate >= 60) return 'c'
  return 'd'
})

const gradeIcon = computed(() => {
  const map = { s: '🏆', a: '🌟', b: '👍', c: '💪', d: '📚' }
  return map[gradeClass.value]
})

const gradeText = computed(() => {
  const map = { s: '优秀', a: '良好', b: '中等', c: '及格', d: '需努力' }
  return map[gradeClass.value]
})

const encouragement = computed(() => {
  const rate = correctRate.value
  if (rate >= 90) return '你的英语基础非常扎实，继续保持！'
  if (rate >= 80) return '表现不错，再接再厉可以更优秀！'
  if (rate >= 60) return '进步空间还很大，继续努力！'
  return '不要气馁，错了就是学习的机会！'
})

const suggestions = computed(() => {
  const list = []
  if (wrongCount.value > 0) {
    list.push('建议针对错题涉及的知识点进行专项复习')
    list.push('可以尝试"错题重练"功能，巩固薄弱环节')
  }
  if (correctRate.value < 80) {
    list.push('每天坚持练习，保持学习节奏')
    list.push('遇到不懂的问题可以向AI助教请教')
  }
  return list
})

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (mins > 0) {
    return `${mins}分${secs}秒`
  }
  return `${secs}秒`
}

function reviewAnswers() {
  router.push({ name: 'Dashboard' })
}

async function generateWrongTest() {
  try {
    const response = await generateWrongTestApi({
      wrong_question_ids: wrongQuestions.value.map(q => q.id || `q${q.index}`),
      difficulty: 'medium'
    })
    router.push({
      name: 'TakeTest',
      params: { testId: response.test_id }
    })
  } catch (error) {
    console.error('生成错题测试失败:', error)
    ElMessage.error('生成失败，请重试')
  }
}

function goHome() {
  router.push({ name: 'Dashboard' })
}
</script>

<style scoped>
.test-result-page {
  min-height: 100%;
  background: #f5f7fa;
  padding: 20px;
}

.score-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  margin-bottom: 20px;
}

.score-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  margin: 0 auto 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.score-circle.excellent {
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  box-shadow: 0 8px 32px rgba(253, 160, 133, 0.3);
}

.score-circle.good {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  box-shadow: 0 8px 32px rgba(132, 250, 176, 0.3);
}

.score-circle.pass {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  box-shadow: 0 8px 32px rgba(161, 196, 253, 0.3);
}

.score-circle.fail {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  box-shadow: 0 8px 32px rgba(255, 154, 158, 0.3);
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.score-total {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
}

.score-info h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #333;
}

.score-info p {
  margin: 0 0 24px;
  color: #999;
  font-size: 14px;
}

.score-stats {
  display: flex;
  justify-content: center;
  gap: 32px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-icon {
  font-size: 24px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.grade-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  margin-bottom: 20px;
}

.grade-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 24px;
  margin-bottom: 12px;
}

.grade-badge.s {
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  color: #fff;
}

.grade-badge.a {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  color: #fff;
}

.grade-badge.b {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  color: #fff;
}

.grade-badge.c {
  background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
  color: #fff;
}

.grade-badge.d {
  background: #f0f0f0;
  color: #666;
}

.grade-icon {
  font-size: 24px;
}

.grade-text {
  font-size: 18px;
  font-weight: 600;
}

.grade-encouragement {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.error-analysis {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}

.error-analysis h3 {
  margin: 0 0 20px;
  font-size: 18px;
  color: #333;
}

.error-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.error-item {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.error-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fef0f0;
  border-bottom: 1px solid #fde2e2;
}

.question-num {
  font-weight: 600;
  color: #f56c6c;
}

.question-type {
  font-size: 12px;
  color: #999;
}

.error-content {
  padding: 16px;
}

.question-display {
  margin-bottom: 16px;
}

.question-text {
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 12px;
  color: #333;
}

.question-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 14px;
}

.option.correct {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
}

.option.wrong {
  background: #fff1f0;
  border: 1px solid #ffa39e;
}

.option-letter {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.option.correct .option-letter {
  background: #52c41a;
  color: #fff;
}

.option.wrong .option-letter {
  background: #f56c6c;
  color: #fff;
}

.analysis-section {
  background: #fafafa;
  padding: 12px;
  border-radius: 8px;
}

.analysis-item {
  display: flex;
  margin-bottom: 8px;
}

.analysis-item:last-child {
  margin-bottom: 0;
}

.analysis-label {
  color: #666;
  font-size: 13px;
  white-space: nowrap;
}

.analysis-value {
  font-size: 13px;
  color: #333;
}

.analysis-value.user-answer {
  color: #f56c6c;
  text-decoration: line-through;
}

.analysis-value.correct-answer {
  color: #52c41a;
  font-weight: 600;
}

.analysis-value.explanation {
  line-height: 1.6;
}

.knowledge-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 12px;
  padding: 6px 12px;
  background: #f0f5ff;
  border-radius: 16px;
  font-size: 12px;
  color: #667eea;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-outline {
  background: #fff;
  color: #666;
  border: 1px solid #e8e8e8;
}

.btn-outline:hover {
  border-color: #667eea;
  color: #667eea;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: #fff;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(56, 239, 125, 0.4);
}

.suggestions {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
}

.suggestions h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #333;
}

.suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.suggestions li {
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.suggestions li:last-child {
  margin-bottom: 0;
}
</style>
