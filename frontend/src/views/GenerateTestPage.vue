<template>
  <Layout>
    <div class="generate-test-page">
      <div class="page-header">
        <h1 class="page-title">生成测试</h1>
        <p class="page-subtitle">选择测试范围和参数，生成个性化测试题</p>
      </div>
      
      <div class="test-form card">
        <el-form :model="form" label-position="top">
          <!-- 选择教材 -->
          <el-form-item label="选择教材" required>
            <el-select v-model="form.textbook_id" placeholder="请选择教材" size="large" style="width: 100%">
              <el-option
                v-for="book in textbooks"
                :key="book.id"
                :label="book.name"
                :value="book.id"
              />
            </el-select>
          </el-form-item>
          
          <!-- 测试类型 -->
          <el-form-item label="测试类型">
            <el-radio-group v-model="form.test_type" size="large">
              <el-radio-button label="unit">单元测试</el-radio-button>
              <el-radio-button label="comprehensive">综合测试</el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <!-- 单元选择（单元测试时显示） -->
          <el-form-item label="选择单元" v-if="form.test_type === 'unit'">
            <el-checkbox-group v-model="form.unit_numbers">
              <el-checkbox v-for="unit in units" :key="unit.id" :label="unit.unit_number">
                {{ unit.title }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          
          <!-- 知识点类型 -->
          <el-form-item label="知识点类型">
            <el-checkbox-group v-model="form.point_types">
              <el-checkbox label="vocabulary">
                <el-icon><Document /></el-icon>
                词汇
              </el-checkbox>
              <el-checkbox label="grammar">
                <el-icon><EditPen /></el-icon>
                语法
              </el-checkbox>
              <el-checkbox label="sentence">
                <el-icon><ChatLineRound /></el-icon>
                句型
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          
          <!-- 难度选择 -->
          <el-form-item label="难度等级">
            <el-radio-group v-model="form.difficulty" size="large">
              <el-radio-button label="easy">简单</el-radio-button>
              <el-radio-button label="medium">中等</el-radio-button>
              <el-radio-button label="hard">困难</el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <!-- 题目数量 -->
          <el-form-item label="题目数量">
            <el-slider 
              v-model="form.question_count" 
              :min="5" 
              :max="30" 
              :step="5"
              :marks="{5: '5', 10: '10', 15: '15', 20: '20', 25: '25', 30: '30'}"
              show-input
            />
            <p class="tip">系统将根据选择范围自动推荐最佳题目数量</p>
          </el-form-item>
          
          <!-- 提交按钮 -->
          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              :loading="generating"
              @click="handleGenerate"
              style="width: 100%"
            >
              <el-icon><EditPen /></el-icon>
              生成测试
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 测试说明 -->
      <div class="test-tips card">
        <h3><el-icon><InfoFilled /></el-icon> 测试说明</h3>
        <ul>
          <li>测试包含选择题、填空题、判断题等多种题型</li>
          <li>每道题目的参考答题时间为2分钟</li>
          <li>测试完成后可查看详细答题报告和错题分析</li>
          <li>系统会自动记录您的测试成绩和学习进度</li>
        </ul>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { getTextbooks } from '@/api/textbooks'
import { getKnowledgePoints } from '@/api/textbooks'
import { generateTest } from '@/api/tests'

const router = useRouter()

const textbooks = ref([])
const units = ref([])
const generating = ref(false)

const form = reactive({
  textbook_id: null,
  test_type: 'unit',
  unit_numbers: [],
  point_types: ['vocabulary', 'grammar', 'sentence'],
  difficulty: 'medium',
  question_count: 15
})

onMounted(async () => {
  await loadTextbooks()
})

watch(() => form.textbook_id, async (newId) => {
  if (newId) {
    await loadUnits(newId)
  }
})

async function loadTextbooks() {
  try {
    textbooks.value = await getTextbooks()
    if (textbooks.value.length > 0) {
      form.textbook_id = textbooks.value[0].id
    }
  } catch (error) {
    ElMessage.error('加载教材列表失败')
  }
}

async function loadUnits(textbookId) {
  try {
    const points = await getKnowledgePoints(textbookId, { page_size: 1000 })
    // 提取单元信息（去重）
    const unitSet = new Set()
    units.value = points.filter(p => {
      if (p.unit_id && !unitSet.has(p.unit_id)) {
        unitSet.add(p.unit_id)
        return true
      }
      return false
    })
  } catch (error) {
    console.error('加载单元失败:', error)
  }
}

async function handleGenerate() {
  if (!form.textbook_id) {
    ElMessage.warning('请选择教材')
    return
  }
  
  if (form.test_type === 'unit' && form.unit_numbers.length === 0) {
    ElMessage.warning('请选择至少一个单元')
    return
  }
  
  if (form.point_types.length === 0) {
    ElMessage.warning('请选择至少一种知识点类型')
    return
  }
  
  generating.value = true
  
  try {
    const result = await generateTest({
      textbook_id: form.textbook_id,
      test_type: form.test_type,
      unit_numbers: form.test_type === 'unit' ? form.unit_numbers : null,
      point_types: form.point_types,
      difficulty: form.difficulty,
      question_count: form.question_count
    })
    
    if (result.test_id) {
      ElMessage.success('测试生成成功！')
      router.push(`/test/${result.test_id}`)
    } else {
      ElMessage.error(result.message || '生成失败')
    }
  } catch (error) {
    ElMessage.error('生成测试失败：' + (error.message || '未知错误'))
  } finally {
    generating.value = false
  }
}
</script>

<style scoped lang="scss">
.generate-test-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.test-form {
  padding: 32px;
  margin-bottom: 24px;
}

.tip {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 8px;
}

.test-tips {
  padding: 24px;
  
  h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    color: var(--primary-color);
  }
  
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    
    li {
      position: relative;
      padding-left: 20px;
      margin-bottom: 8px;
      font-size: 14px;
      color: var(--text-regular);
      
      &::before {
        content: '•';
        position: absolute;
        left: 0;
        color: var(--primary-color);
      }
    }
  }
}
</style>
