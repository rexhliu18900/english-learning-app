<template>
  <Layout>
    <div class="textbooks-page">
      <div class="page-header">
        <div>
          <h1 class="page-title">我的教材</h1>
          <p class="page-subtitle">管理您的英语学习教材</p>
        </div>
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon>
          上传教材
        </el-button>
      </div>
      
      <!-- 教材列表 -->
      <div class="textbook-list" v-if="textbooks.length > 0">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :lg="8" v-for="book in textbooks" :key="book.id">
            <div class="textbook-card card" @click="viewTextbook(book)">
              <div class="textbook-icon">
                <el-icon size="48"><Document /></el-icon>
              </div>
              <div class="textbook-info">
                <h3>{{ book.name }}</h3>
                <p class="textbook-version" v-if="book.version">版本：{{ book.version }}</p>
                <el-tag :type="getStatusType(book.parse_status)" size="small">
                  {{ getStatusText(book.parse_status) }}
                </el-tag>
              </div>
              <div class="textbook-actions" @click.stop>
                <el-dropdown trigger="click">
                  <el-icon size="20"><MoreFilled /></el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="viewTextbook(book)">
                        <el-icon><View /></el-icon>
                        查看详情
                      </el-dropdown-item>
                      <el-dropdown-item 
                        v-if="book.parse_status === 'pending'" 
                        @click="parseBook(book)"
                      >
                        <el-icon><DocumentCopy /></el-icon>
                        解析教材
                      </el-dropdown-item>
                      <el-dropdown-item 
                        divided 
                        @click="deleteBook(book)"
                        type="danger"
                      >
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              <div class="textbook-stats" v-if="book.statistics">
                <span>词汇 {{ book.statistics.vocabulary_count || 0 }}</span>
                <span v-if="book.statistics.grammar_count">语法 {{ book.statistics.grammar_count }}</span>
                <span v-if="book.statistics.sentence_count">句型 {{ book.statistics.sentence_count }}</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 空状态 -->
      <el-empty v-else description="暂无教材">
        <el-button type="primary" @click="showUploadDialog = true">
          上传第一本教材
        </el-button>
      </el-empty>
      
      <!-- 上传对话框 -->
      <el-dialog
        v-model="showUploadDialog"
        title="上传教材"
        width="500px"
      >
        <el-form :model="uploadForm" label-position="top">
          <el-form-item label="教材名称" required>
            <el-input v-model="uploadForm.name" placeholder="例如：人教版八年级下册英语" />
          </el-form-item>
          <el-form-item label="教材版本（可选）">
            <el-input v-model="uploadForm.version" placeholder="例如：2025年版" />
          </el-form-item>
          <el-form-item label="教材文件" required>
            <el-upload
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept=".pdf,.docx,.doc,.md"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处，或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 PDF、Word、Markdown 格式
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showUploadDialog = false">取消</el-button>
          <el-button type="primary" :loading="uploading" @click="handleUpload">
            上传并解析
          </el-button>
        </template>
      </el-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { getTextbooks, uploadTextbook, parseTextbook, deleteTextbook } from '@/api/textbooks'

const router = useRouter()

const textbooks = ref([])
const showUploadDialog = ref(false)
const uploading = ref(false)
const uploadForm = reactive({
  name: '',
  version: '',
  file: null
})

onMounted(async () => {
  await loadTextbooks()
})

async function loadTextbooks() {
  try {
    textbooks.value = await getTextbooks()
  } catch (error) {
    ElMessage.error('加载教材列表失败')
  }
}

function handleFileChange(file) {
  uploadForm.file = file.raw
}

async function handleUpload() {
  if (!uploadForm.name) {
    ElMessage.warning('请输入教材名称')
    return
  }
  
  if (!uploadForm.file) {
    ElMessage.warning('请选择教材文件')
    return
  }
  
  uploading.value = true
  
  try {
    const result = await uploadTextbook(
      uploadForm.file,
      uploadForm.name,
      uploadForm.version || null
    )
    
    if (result.success) {
      ElMessage.success('教材上传成功！')
      showUploadDialog.value = false
      
      // 自动开始解析
      await parseBook({ id: result.textbook.id })
    } else {
      ElMessage.error(result.message || '上传失败')
    }
  } catch (error) {
    ElMessage.error('上传失败：' + (error.message || '未知错误'))
  } finally {
    uploading.value = false
  }
}

async function parseBook(book) {
  try {
    const result = await parseTextbook(book.id)
    if (result.success) {
      ElMessage.success('教材解析成功！')
      await loadTextbooks()
    } else {
      ElMessage.error(result.message || '解析失败')
    }
  } catch (error) {
    ElMessage.error('解析失败')
  }
}

async function deleteBook(book) {
  try {
    await ElMessageBox.confirm(
      `确定要删除《${book.name}》吗？此操作不可恢复。`,
      '删除确认',
      { type: 'warning' }
    )
    
    await deleteTextbook(book.id)
    ElMessage.success('删除成功')
    await loadTextbooks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function viewTextbook(book) {
  router.push(`/textbooks/${book.id}`)
}

function getStatusType(status) {
  const types = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = {
    pending: '待解析',
    processing: '解析中',
    completed: '已解析',
    failed: '解析失败'
  }
  return texts[status] || status
}
</script>

<style scoped lang="scss">
.textbooks-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.textbook-card {
  display: flex;
  align-items: center;
  padding: 24px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  }
}

.textbook-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 20px;
}

.textbook-info {
  flex: 1;
  
  h3 {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--text-primary);
  }
  
  .textbook-version {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 8px;
  }
}

.textbook-actions {
  position: absolute;
  top: 16px;
  right: 16px;
  color: var(--text-secondary);
  cursor: pointer;
}

.textbook-stats {
  position: absolute;
  bottom: 16px;
  right: 16px;
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
