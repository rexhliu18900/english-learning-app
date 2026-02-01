<template>
  <div class="chat-page">
    <div class="chat-header">
      <h2>AI 智能助教</h2>
      <span class="subtitle">基于教材内容的智能问答</span>
    </div>

    <div class="chat-container" ref="chatContainer">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        <h3>你好！我是你的 AI 智能助教</h3>
        <p>我可以帮助你解答英语学习中的各种问题，包括：</p>
        <ul>
          <li>词汇解释和用法</li>
          <li>语法知识讲解</li>
          <li>句型结构分析</li>
          <li>阅读理解答疑</li>
          <li>写作指导建议</li>
        </ul>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
        <div class="message-avatar">
          <span v-if="msg.role === 'assistant'" class="avatar-emoji">🤖</span>
          <span v-else class="avatar-emoji">👤</span>
        </div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(msg.content)"></div>
          <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="message assistant loading">
        <div class="message-avatar">
          <span class="avatar-emoji">🤖</span>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速问题 -->
    <div class="quick-questions" v-if="messages.length < 3">
      <span class="quick-label">试试这样问：</span>
      <span class="quick-question" v-for="q in quickQuestions" :key="q" @click="askQuickQuestion(q)">
        {{ q }}
      </span>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-wrapper">
        <textarea
          v-model="userInput"
          placeholder="输入你的问题..."
          @keydown.enter.exact.prevent="sendMessage"
          :rows="1"
          ref="inputRef"
        ></textarea>
        <button class="send-btn" @click="sendMessage" :disabled="!userInput.trim() || isLoading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
      <div class="input-hint">按 Enter 发送，Shift+Enter 换行</div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { chat, queryKnowledge } from '@/api/chat'
import { formatTime } from '@/utils'

const router = useRouter()
const chatContainer = ref(null)
const inputRef = ref(null)
const userInput = ref('')
const messages = ref([])
const isLoading = ref(false)

const quickQuestions = [
  '这个单元的重点词汇有哪些？',
  '帮我解释一下现在完成时的用法',
  '怎么区分 since 和 for 的用法？',
  '给我讲讲被动语态的构成',
]

onMounted(() => {
  scrollToBottom()
})

watch(messages.value, () => {
  nextTick(() => scrollToBottom())
})

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

function formatMessage(content) {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

async function askQuickQuestion(question) {
  userInput.value = question
  await sendMessage()
}

async function sendMessage() {
  const content = userInput.value.trim()
  if (!content || isLoading.value) return

  messages.value.push({
    role: 'user',
    content,
    timestamp: new Date()
  })

  userInput.value = ''
  isLoading.value = true

  try {
    const response = await chat({
      message: content,
      history: messages.value.slice(-10).map(m => ({
        role: m.role,
        content: m.content
      }))
    })

    messages.value.push({
      role: 'assistant',
      content: response.answer || response.message || '抱歉，我暂时无法回答这个问题。',
      timestamp: new Date()
    })
  } catch (error) {
    console.error('Chat error:', error)
    ElMessage.error('问答失败，请稍后重试')
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题。请稍后再试，或者尝试重新表述您的问题。',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
    nextTick(() => scrollToBottom())
  }
}
</script>

<style scoped>
.chat-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.chat-header {
  padding: 20px 24px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
}

.chat-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.chat-header .subtitle {
  font-size: 13px;
  color: #999;
  margin-top: 4px;
  display: block;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 20px;
}

.welcome-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-icon svg {
  width: 32px;
  height: 32px;
  color: #fff;
}

.welcome-message h3 {
  margin: 0 0 12px;
  color: #333;
  font-size: 18px;
}

.welcome-message p {
  color: #666;
  margin: 0 0 16px;
}

.welcome-message ul {
  text-align: left;
  display: inline-block;
  margin: 0;
  padding-left: 20px;
  color: #666;
}

.welcome-message li {
  margin: 8px 0;
}

.message {
  display: flex;
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.assistant {
  flex-direction: row;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-emoji {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  font-size: 24px;
  border-radius: 50%;
  background: #f0f0f0;
}

.message-content {
  max-width: 70%;
  margin: 0 12px;
}

.message-text {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.message.assistant .message-text {
  background: #fff;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: #bbb;
  margin-top: 4px;
}

.message.user .message-time {
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #ccc;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.quick-questions {
  padding: 12px 20px;
  background: #fff;
  border-top: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-label {
  font-size: 12px;
  color: #999;
}

.quick-question {
  padding: 6px 12px;
  background: #f0f2f5;
  border-radius: 16px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-question:hover {
  background: #e8eaf6;
  color: #667eea;
}

.input-area {
  padding: 16px 20px 24px;
  background: #fff;
  border-top: 1px solid #e8e8e8;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  background: #f5f7fa;
  border-radius: 24px;
  padding: 8px 8px 8px 20px;
}

.input-wrapper textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  max-height: 100px;
  outline: none;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 18px;
  height: 18px;
}

.input-hint {
  font-size: 11px;
  color: #bbb;
  text-align: center;
  margin-top: 8px;
}
</style>
