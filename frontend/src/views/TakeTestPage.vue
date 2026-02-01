<template>
  <div class="take-test-page">
    <div class="test-header">
      <div class="test-info">
        <h2>{{ testInfo.title }}</h2>
        <span class="test-meta">
          {{ testInfo.questionCount }} 题 | 预计 {{ testInfo.duration }} 分钟 | {{ difficultyText }}
        </span>
      </div>
      <div class="timer" v-if="timeRemaining">
        <span class="timer-icon">⏱</span>
        <span class="timer-value">{{ formatTime(timeRemaining) }}</span>
      </div>
    </div>

    <div class="test-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <span class="progress-text">{{ currentIndex + 1 }} / {{ questions.length }}</span>
    </div>

    <div class="question-card" v-if="questions.length > 0">
      <!-- 题目标题 -->
      <div class="question-header">
        <span class="question-type">{{ questionTypeText }}</span>
        <span class="question-score">本题 {{ question.score }} 分</span>
      </div>

      <!-- 问题内容 -->
      <div class="question-content">
        <div class="question-text" v-html="question.question"></div>
        <div class="question-options" v-if="question.options && question.options.length > 0">
          <div
            v-for="(option, idx) in question.options"
            :key="idx"
            :class="['option-item', { selected: answers[question.id] === idx }]"
            @click="selectAnswer(idx)"
          >
            <span class="option-letter">{{ String.fromCharCode(65 + idx) }}</span>
            <span class="option-text" v-html="option"></span>
          </div>
        </div>
        <!-- 填空题/其他题型 -->
        <div class="fill-in-input" v-if="question.type === 'fill_in'">
          <input
            type="text"
            v-model="fillInAnswers[question.id]"
            :placeholder="question.placeholder || '请输入答案...'"
          />
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="test-actions">
      <button
        class="btn btn-secondary"
        @click="prevQuestion"
        :disabled="currentIndex === 0"
      >
        上一题
      </button>
      <button
        v-if="currentIndex < questions.length - 1"
        class="btn btn-primary"
        @click="nextQuestion"
      >
        下一题
      </button>
      <button
        v-else
        class="btn btn-success"
        @click="submitTest"
        :disabled="submitting"
      >
        {{ submitting ? '提交中...' : '提交答卷' }}
      </button>
    </div>

    <!-- 题目导航 -->
    <div class="question-nav">
      <span class="nav-label">题目导航：</span>
      <div class="nav-dots">
        <span
          v-for="(q, idx) in questions"
          :key="q.id"
          :class="['nav-dot', {
            current: idx === currentIndex,
            answered: isAnswered(q.id),
            current_answered: idx === currentIndex && isAnswered(q.id)
          }]"
          @click="goToQuestion(idx)"
        >
          {{ idx + 1 }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTest, submitTest as submitTestApi } from '@/api/tests'

const router = useRouter()
const route = useRoute()

const testInfo = ref({
  title: '综合测试',
  questionCount: 0,
  duration: 10
})

const questions = ref([])
const currentIndex = ref(0)
const answers = ref({})
const fillInAnswers = ref({})
const timeRemaining = ref(null)
const timer = ref(null)
const submitting = ref(false)
const testId = ref(route.params.testId || null)
const testData = ref(null)

const question = computed(() => questions.value[currentIndex.value] || {})

const progressPercent = computed(() => {
  if (questions.value.length === 0) return 0
  return ((currentIndex.value + 1) / questions.value.length) * 100
})

const difficultyText = computed(() => {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return map[testInfo.value.difficulty] || '中等'
})

const questionTypeText = computed(() => {
  const map = {
    choice: '选择题',
    fill_in: '填空题',
    true_false: '判断题',
    contextual: '阅读理解',
    matching: '配对题'
  }
  return map[question.value.type] || '选择题'
})

onMounted(async () => {
  await loadTest()
  startTimer()
})

onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})

async function loadTest() {
  try {
    if (testId.value) {
      // 从服务器加载测试
      const response = await getTest(testId.value)
      testData.value = response
      testInfo.value = {
        title: response.title || '测试',
        questionCount: response.questions?.length || 0,
        duration: response.estimated_time || 10,
        difficulty: response.difficulty
      }
      questions.value = response.questions || []
    } else {
      // 模拟测试数据（用于演示）
      questions.value = generateMockQuestions()
      testInfo.value = {
        title: 'Unit 1-2 综合测试',
        questionCount: questions.value.length,
        duration: 15,
        difficulty: 'medium'
      }
    }
  } catch (error) {
    console.error('加载测试失败:', error)
    ElMessage.error('加载测试失败')
    questions.value = generateMockQuestions()
  }
}

function generateMockQuestions() {
  return [
    {
      id: 'q1',
      type: 'choice',
      question: 'What ___ you ___ when the phone rang?',
      options: ['were...doing', 'are...doing', 'did...do', 'do...do'],
      answer: 0,
      score: 5,
      knowledge_point: '过去进行时'
    },
    {
      id: 'q2',
      type: 'choice',
      question: 'She has lived in Beijing ___ 2010.',
      options: ['since', 'for', 'in', 'at'],
      answer: 0,
      score: 5,
      knowledge_point: 'since/for 区别'
    },
    {
      id: 'q3',
      type: 'true_false',
      question: 'The passive voice is formed with "be + past participle".',
      answer: 1,
      score: 5,
      knowledge_point: '被动语态'
    },
    {
      id: 'q4',
      type: 'fill_in',
      question: 'Fill in the blank: The book ___ (read) by Mary.',
      answer: 'is read',
      score: 5,
      knowledge_point: '被动语态'
    },
    {
      id: 'q5',
      type: 'choice',
      question: '___ volume please? I can\'t hear clearly.',
      options: ['Can you turn up', 'Can you turn down', 'Could you turn up', 'Could you turn down'],
      answer: 2,
      score: 5,
      knowledge_point: '情态动词'
    }
  ]
}

function isAnswered(questionId) {
  if (questions.value[currentIndex.value]?.type === 'fill_in') {
    return fillInAnswers.value[questionId]?.trim() !== ''
  }
  return answers.value[questionId] !== undefined
}

function selectAnswer(index) {
  answers.value[question.value.id] = index
}

function prevQuestion() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

function nextQuestion() {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  }
}

function goToQuestion(index) {
  currentIndex.value = index
}

function startTimer() {
  timeRemaining.value = testInfo.value.duration * 60
  timer.value = setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--
    } else {
      clearInterval(timer.value)
      ElMessage.warning('时间到！正在自动提交...')
      submitTest()
    }
  }, 1000)
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

async function submitTest() {
  if (submitting.value) return
  submitting.value = true

  try {
    const answersData = questions.value.map(q => ({
      question_id: q.id,
      answer: q.type === 'fill_in' ? (fillInAnswers.value[q.id] || '') : answers.value[q.id],
      is_correct: checkAnswer(q)
    }))

    const payload = {
      test_id: testData.value?.id,
      answers: answersData,
      time_spent: (testInfo.value.duration * 60) - timeRemaining.value
    }

    if (testId.value) {
      await submitTestApi(payload)
    }

    // 计算分数
    const correctCount = answersData.filter(a => a.is_correct).length
    const totalScore = questions.value.reduce((sum, q) => sum + q.score, 0)
    const earnedScore = answersData.filter(a => a.is_correct).reduce((sum, q) => {
      const question = questions.value.find(x => x.id === q.question_id)
      return sum + (question?.score || 0)
    }, 0)

    router.push({
      name: 'TestResult',
      params: {
        correctCount,
        totalCount: questions.value.length,
        score: earnedScore,
        totalScore,
        timeSpent: payload.time_spent
      }
    })
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请重试')
    submitting.value = false
  }
}

function checkAnswer(question) {
  if (question.type === 'fill_in') {
    const userAnswer = (fillInAnswers.value[question.id] || '').toLowerCase().trim()
    const correctAnswer = (question.answer || '').toLowerCase().trim()
    return userAnswer === correctAnswer
  }
  return answers.value[question.id] === question.answer
}
</script>

<style scoped>
.take-test-page {
  min-height: 100%;
  background: #f5f7fa;
  padding: 20px;
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.test-info h2 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #333;
}

.test-meta {
  font-size: 13px;
  color: #999;
}

.timer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #fef0f0;
  border-radius: 20px;
  color: #f56c6c;
  font-weight: 600;
}

.timer-icon {
  font-size: 16px;
}

.test-progress {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e8e8e8;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.question-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  min-height: 300px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.question-type {
  padding: 4px 12px;
  background: #f0f5ff;
  color: #667eea;
  border-radius: 4px;
  font-size: 12px;
}

.question-score {
  font-size: 12px;
  color: #999;
}

.question-content {
  font-size: 16px;
  line-height: 1.8;
}

.question-text {
  margin-bottom: 24px;
  color: #333;
}

.question-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border: 2px solid #e8e8e8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  border-color: #667eea;
  background: #f5f7ff;
}

.option-item.selected {
  border-color: #667eea;
  background: #f0f5ff;
}

.option-letter {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 50%;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.option-item.selected .option-letter {
  background: #667eea;
  color: #fff;
}

.option-text {
  flex: 1;
}

.fill-in-input input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e8e8e8;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.fill-in-input input:focus {
  outline: none;
  border-color: #667eea;
}

.test-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.btn {
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #fff;
  color: #666;
  border: 1px solid #e8e8e8;
}

.btn-secondary:hover:not(:disabled) {
  border-color: #667eea;
  color: #667eea;
}

.btn-success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: #fff;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(56, 239, 125, 0.4);
}

.question-nav {
  background: #fff;
  padding: 16px 20px;
  border-radius: 12px;
}

.nav-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 12px;
  display: block;
}

.nav-dots {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.nav-dot {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 13px;
  cursor: pointer;
  background: #f0f0f0;
  color: #666;
  transition: all 0.2s;
}

.nav-dot:hover {
  background: #e8e8e8;
}

.nav-dot.current {
  background: #667eea;
  color: #fff;
}

.nav-dot.answered {
  background: #f0f5ff;
  color: #667eea;
}

.nav-dot.current_answered {
  background: #667eea;
  color: #fff;
}
</style>
