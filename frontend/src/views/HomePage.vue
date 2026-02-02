<template>
  <Layout>
    <div class="home-page">
      <!-- 英雄区域 -->
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">AI赋能英语学习</h1>
          <p class="hero-subtitle">
            智能教材解析 · 个性化测试生成 · 精准错题分析
            <br>帮助孩子高效掌握英语知识
          </p>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="goToRegister">
              立即开始学习
            </el-button>
            <el-button size="large" @click="goToLogin">
              已有账号，去登录
            </el-button>
          </div>
        </div>
        <div class="hero-image">
          <img src="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=500" alt="英语学习" />
        </div>
      </section>
      
      <!-- 功能特点 -->
      <section class="features-section">
        <h2 class="section-title">核心功能</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon size="40"><Document /></el-icon>
            </div>
            <h3>智能教材解析</h3>
            <p>支持PDF、Word格式教材，自动提取词汇、语法、句型等知识点</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon size="40"><ChatDotRound /></el-icon>
            </div>
            <h3>AI智能对话</h3>
            <p>基于教材内容的智能问答，随时解答学习疑问</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon size="40"><EditPen /></el-icon>
            </div>
            <h3>个性化测试</h3>
            <p>根据学习进度智能生成测试题，支持多种题型</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon size="40"><TrendCharts /></el-icon>
            </div>
            <h3>学习统计</h3>
            <p>详细记录学习轨迹，可视化展示薄弱知识点</p>
          </div>
        </div>
      </section>
      
      <!-- 使用流程 -->
      <section class="process-section">
        <h2 class="section-title">使用流程</h2>
        <div class="process-steps">
          <div class="step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h4>上传教材</h4>
              <p>上传英语教材文件（PDF/Word）</p>
            </div>
          </div>
          <div class="step-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h4>智能解析</h4>
              <p>自动提取知识点结构</p>
            </div>
          </div>
          <div class="step-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h4>对话学习</h4>
              <p>AI问答掌握知识点</p>
            </div>
          </div>
          <div class="step-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
          <div class="step">
            <div class="step-number">4</div>
            <div class="step-content">
              <h4>测试巩固</h4>
              <p>生成测试检验学习效果</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </Layout>
</template>

<script setup>
import Layout from '@/components/Layout.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const goToRegister = () => {
  router.push('/register')
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped lang="scss">
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  display: flex;
  align-items: center;
  gap: 60px;
  padding: 60px 20px;
  min-height: 500px;
}

.hero-content {
  flex: 1;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 32px;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.hero-image {
  flex: 1;
  
  img {
    width: 100%;
    max-width: 450px;
    border-radius: 16px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  }
}

.features-section {
  padding: 60px 20px;
  background: #fff;
}

.section-title {
  font-size: 32px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 48px;
  color: var(--text-primary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.feature-card {
  text-align: center;
  padding: 32px 24px;
  border-radius: 12px;
  background: var(--bg-color);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  }
}

.feature-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border-radius: 50%;
  color: #fff;
}

.feature-card h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.feature-card p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.process-section {
  padding: 60px 20px;
}

.process-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.step {
  text-align: center;
}

.step-number {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  border-radius: 50%;
}

.step-content h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.step-content p {
  font-size: 14px;
  color: var(--text-secondary);
}

.step-arrow {
  color: var(--text-secondary);
  font-size: 24px;
}

@media (max-width: 992px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
    gap: 40px;
  }
  
  .hero-actions {
    justify-content: center;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .process-steps {
    flex-wrap: wrap;
  }
  
  .step-arrow {
    display: none;
  }
}

@media (max-width: 576px) {
  .hero-title {
    font-size: 32px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
