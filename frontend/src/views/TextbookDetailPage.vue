<template>
  <div class="textbook-detail-page">
    <!-- 教材头部信息 -->
    <div class="textbook-header">
      <div class="header-back" @click="goBack">
        <span class="back-icon">←</span>
        <span>返回</span>
      </div>
      <div class="textbook-info">
        <h1>{{ textbook.title }}</h1>
        <p class="textbook-meta">{{ textbook.grade }} | {{ textbook.publisher }}</p>
      </div>
    </div>

    <!-- 单元列表 -->
    <div class="units-section">
      <h2>📖 单元列表</h2>
      <div class="units-grid">
        <div
          v-for="unit in units"
          :key="unit.id"
          class="unit-card"
          :class="{ expanded: expandedUnit === unit.id }"
          @click="toggleUnit(unit.id)"
        >
          <div class="unit-header">
            <div class="unit-info">
              <span class="unit-number">Unit {{ unit.number }}</span>
              <span class="unit-title">{{ unit.title }}</span>
            </div>
            <span class="expand-icon">{{ expandedUnit === unit.id ? '−' : '+' }}</span>
          </div>
          
          <div class="unit-content" v-show="expandedUnit === unit.id">
            <div class="knowledge-categories">
              <!-- 词汇 -->
              <div class="category-card">
                <div class="category-header">
                  <span class="category-icon">📝</span>
                  <span class="category-name">重点词汇</span>
                  <span class="category-count">{{ unit.vocabulary.length }} 个</span>
                </div>
                <div class="category-content">
                  <div class="vocabulary-list">
                    <div
                      v-for="(word, idx) in unit.vocabulary.slice(0, 5)"
                      :key="idx"
                      class="vocabulary-item"
                      @click.stop="showWordDetail(word)"
                    >
                      <span class="word">{{ word.word }}</span>
                      <span class="phonetic">{{ word.phonetic }}</span>
                      <span class="part-of-speech">{{ word.part }}</span>
                    </div>
                    <button
                      class="show-more"
                      v-if="unit.vocabulary.length > 5"
                      @click.stop="showAllVocabulary(unit)"
                    >
                      查看全部 {{ unit.vocabulary.length }} 个词汇
                    </button>
                  </div>
                </div>
              </div>

              <!-- 语法 -->
              <div class="category-card">
                <div class="category-header">
                  <span class="category-icon">📐</span>
                  <span class="category-name">语法知识</span>
                  <span class="category-count">{{ unit.grammar.length }} 个</span>
                </div>
                <div class="category-content">
                  <div class="grammar-list">
                    <div
                      v-for="(gram, idx) in unit.grammar"
                      :key="idx"
                      class="grammar-item"
                      @click.stop="showGrammarDetail(gram)"
                    >
                      <span class="grammar-name">{{ gram.name }}</span>
                      <span class="grammar-desc">{{ gram.description }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 句型 -->
              <div class="category-card">
                <div class="category-header">
                  <span class="category-icon">💬</span>
                  <span class="category-name">重点句型</span>
                  <span class="category-count">{{ unit.sentences.length }} 个</span>
                </div>
                <div class="category-content">
                  <div class="sentence-list">
                    <div
                      v-for="(sent, idx) in unit.sentences"
                      :key="idx"
                      class="sentence-item"
                    >
                      <div class="sentence-chinese">{{ sent.chinese }}</div>
                      <div class="sentence-english">{{ sent.english }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 快捷操作 -->
            <div class="unit-actions">
              <button class="action-btn" @click.stop="startLearning(unit)">
                <span>📚</span> 开始学习
              </button>
              <button class="action-btn" @click.stop="generateUnitTest(unit)">
                <span>📝</span> 单元测试
              </button>
              <button class="action-btn" @click.stop="askAI(unit)">
                <span>🤖</span> 向AI提问
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 词汇详情抽屉 -->
    <el-drawer v-model="showWordDrawer" title="词汇详情" size="50%">
      <div class="word-detail" v-if="currentWord">
        <div class="word-header">
          <h2>{{ currentWord.word }}</h2>
          <span class="phonetic">{{ currentWord.phonetic }}</span>
          <span class="part-of-speech">{{ currentWord.part }}</span>
        </div>
        <div class="word-meaning">
          <h4>释义</h4>
          <p>{{ currentWord.meaning }}</p>
        </div>
        <div class="word-example" v-if="currentWord.examples">
          <h4>例句</h4>
          <div v-for="(ex, idx) in currentWord.examples" :key="idx" class="example-item">
            <p class="example-english">{{ ex.english }}</p>
            <p class="example-chinese">{{ ex.chinese }}</p>
          </div>
        </div>
        <div class="word-synonyms" v-if="currentWord.synonyms">
          <h4>同义词</h4>
          <div class="tag-list">
            <span class="tag" v-for="syn in currentWord.synonyms" :key="syn">{{ syn }}</span>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 语法详情抽屉 -->
    <el-drawer v-model="showGrammarDrawer" title="语法详情" size="50%">
      <div class="grammar-detail" v-if="currentGrammar">
        <div class="grammar-header">
          <h2>{{ currentGrammar.name }}</h2>
        </div>
        <div class="grammar-usage">
          <h4>用法</h4>
          <p>{{ currentGrammar.usage }}</p>
        </div>
        <div class="grammar-structure">
          <h4>结构</h4>
          <pre>{{ currentGrammar.structure }}</pre>
        </div>
        <div class="grammar-examples" v-if="currentGrammar.examples">
          <h4>例句</h4>
          <div v-for="(ex, idx) in currentGrammar.examples" :key="idx" class="example-item">
            <p class="example-english">{{ ex.english }}</p>
            <p class="example-chinese">{{ ex.chinese }}</p>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 全部词汇抽屉 -->
    <el-drawer v-model="showAllVocabDrawer" :title="`${currentUnit?.title} - 全部词汇`" size="70%">
      <div class="all-vocabulary">
        <div class="vocab-search">
          <input
            type="text"
            v-model="vocabSearch"
            placeholder="搜索词汇..."
          />
        </div>
        <div class="vocab-filter">
          <button
            v-for="letter in alphabet"
            :key="letter"
            :class="['letter-btn', { active: vocabFilter === letter }]"
            @click="vocabFilter = vocabFilter === letter ? '' : letter"
          >
            {{ letter }}
          </button>
        </div>
        <div class="vocab-list">
          <div
            v-for="word in filteredVocabList"
            :key="word.word"
            class="vocab-item"
            @click="showWordDetail(word)"
          >
            <span class="word">{{ word.word }}</span>
            <span class="phonetic">{{ word.phonetic }}</span>
            <span class="part">{{ word.part }}</span>
            <span class="meaning">{{ word.meaning }}</span>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const expandedUnit = ref(null)
const showWordDrawer = ref(false)
const showGrammarDrawer = ref(false)
const showAllVocabDrawer = ref(false)
const currentWord = ref(null)
const currentGrammar = ref(null)
const currentUnit = ref(null)
const vocabSearch = ref('')
const vocabFilter = ref('')

const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

const textbook = ref({
  id: 'textbook_1',
  title: '人教版八年级下册英语',
  grade: '八年级',
  publisher: '人民教育出版社'
})

// 模拟单元数据
const units = ref([
  {
    id: 'unit_1',
    number: 1,
    title: "What's the matter?",
    vocabulary: [
      { word: 'matter', phonetic: '/ˈmætə(r)/', part: 'n.', meaning: '问题；事情', examples: [{ english: 'What\'s the matter?', chinese: '怎么了？' }] },
      { word: 'hurt', phonetic: '/hɜːt/', part: 'v.', meaning: '使疼痛；受伤', examples: [{ english: 'My head hurts.', chinese: '我头疼。' }] },
      { word: 'fall', phonetic: '/fɔːl/', part: 'v.', meaning: '摔倒；落下', examples: [{ english: 'She fell down the stairs.', chinese: '她从楼梯上摔下来了。' }] },
      { word: 'cut', phonetic: '/kʌt/', part: 'v.', meaning: '切；割', examples: [{ english: 'I cut my finger.', chinese: '我切到了手指。' }] },
      { word: 'hit', phonetic: '/hɪt/', part: 'v.', meaning: '打；撞击', examples: [{ english: 'The car hit the tree.', chinese: '汽车撞到了树上。' }] },
      { word: 'nose', phonetic: '/nəʊz/', part: 'n.', meaning: '鼻子', examples: [{ english: 'My nose is running.', chinese: '我在流鼻涕。' }] },
      { word: 'feel', phonetic: '/fiːl/', part: 'v.', meaning: '感觉；觉得', examples: [{ english: 'How do you feel?', chinese: '你感觉怎么样？' }] }
    ],
    grammar: [
      { name: '现在进行时表将来', usage: '表示已经计划好的将来动作，常与动词go, come, leave, start等连用', structure: '主语 + be + 动词ing形式', examples: [{ english: 'I am coming to see you tomorrow.', chinese: '我明天要来看你。' }] },
      { name: '祈使句', usage: '表示命令、请求或建议的句子', structure: '动词原形...', examples: [{ english: 'Please sit down.', chinese: '请坐。' }] }
    ],
    sentences: [
      { chinese: '你怎么了？', english: 'What\'s the matter?' },
      { chinese: '我发烧了。', english: 'I have a fever.' },
      { chinese: '你应该多喝热水。', english: 'You should drink more hot water.' }
    ]
  },
  {
    id: 'unit_2',
    number: 2,
    title: "I'll help to clean up the city parks.",
    vocabulary: [
      { word: 'clean up', phonetic: '/kliːn ʌp/', part: 'v.', meaning: '打扫干净', examples: [{ english: 'Let\'s clean up the room.', chinese: '让我们把房间打扫干净。' }] },
      { word: 'volunteer', phonetic: '/ˌvɒlənˈtɪə(r)/', part: 'n./v.', meaning: '志愿者；自愿', examples: [{ english: 'He volunteers at the hospital.', chinese: '他在医院做志愿者。' }] },
      { word: 'sign', phonetic: '/saɪn/', part: 'n./v.', meaning: '标志；签名', examples: [{ english: 'Please sign here.', chinese: '请在这里签名。' }] }
    ],
    grammar: [
      { name: '一般将来时', usage: '表示将来要发生的动作或状态', structure: 'will + 动词原形 / be going to + 动词原形', examples: [{ english: 'I will help you.', chinese: '我会帮助你。' }] }
    ],
    sentences: [
      { chinese: '我将帮助清理城市公园。', english: 'I\'ll help to clean up the city parks.' },
      { chinese: '你可以让我振作起来。', english: 'You cheer me up.' }
    ]
  }
])

const filteredVocabList = computed(() => {
  let list = currentUnit.value?.vocabulary || []
  if (vocabFilter.value) {
    list = list.filter(w => w.word.toUpperCase().startsWith(vocabFilter.value))
  }
  if (vocabSearch.value) {
    list = list.filter(w => w.word.toLowerCase().includes(vocabSearch.value.toLowerCase()))
  }
  return list
})

function goBack() {
  router.push({ name: 'Textbooks' })
}

function toggleUnit(unitId) {
  expandedUnit.value = expandedUnit.value === unitId ? null : unitId
}

function showWordDetail(word) {
  currentWord.value = word
  showWordDrawer.value = true
}

function showGrammarDetail(grammar) {
  currentGrammar.value = grammar
  showGrammarDrawer.value = true
}

function showAllVocabulary(unit) {
  currentUnit.value = unit
  vocabSearch.value = ''
  vocabFilter.value = ''
  showAllVocabDrawer.value = true
}

function startLearning(unit) {
  router.push({ name: 'Chat', query: { unit: unit.id } })
}

function generateUnitTest(unit) {
  router.push({
    name: 'GenerateTest',
    query: { unit: unit.number, type: 'unit' }
  })
}

function askAI(unit) {
  router.push({
    name: 'Chat',
    query: { unit: unit.id, focus: 'grammar' }
  })
}
</script>

<style scoped>
.textbook-detail-page {
  min-height: 100%;
  background: #f5f7fa;
}

.textbook-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  color: #fff;
}

.header-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-bottom: 16px;
  opacity: 0.9;
}

.header-back:hover {
  opacity: 1;
}

.textbook-info h1 {
  margin: 0 0 8px;
  font-size: 22px;
}

.textbook-meta {
  margin: 0;
  opacity: 0.8;
  font-size: 14px;
}

.units-section {
  padding: 20px;
}

.units-section h2 {
  margin: 0 0 20px;
  font-size: 18px;
  color: #333;
}

.units-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.unit-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.unit-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.unit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.unit-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.unit-number {
  padding: 4px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
}

.unit-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.expand-icon {
  font-size: 20px;
  color: #999;
}

.unit-content {
  padding: 0 20px 20px;
}

.knowledge-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.category-card {
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f0f0f0;
}

.category-icon {
  font-size: 18px;
}

.category-name {
  flex: 1;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.category-count {
  font-size: 12px;
  color: #999;
}

.category-content {
  padding: 12px;
}

.vocabulary-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.vocabulary-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.vocabulary-item:hover {
  background: #f0f5ff;
}

.vocabulary-item .word {
  font-weight: 600;
  color: #333;
  min-width: 80px;
}

.vocabulary-item .phonetic {
  font-size: 12px;
  color: #999;
  min-width: 70px;
}

.vocabulary-item .part-of-speech {
  font-size: 11px;
  color: #667eea;
  background: #f0f5ff;
  padding: 2px 6px;
  border-radius: 3px;
}

.show-more {
  width: 100%;
  padding: 8px;
  background: transparent;
  border: 1px dashed #ddd;
  border-radius: 4px;
  color: #667eea;
  font-size: 12px;
  cursor: pointer;
  margin-top: 8px;
}

.show-more:hover {
  border-color: #667eea;
  background: #f0f5ff;
}

.grammar-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.grammar-item {
  padding: 10px;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.grammar-item:hover {
  background: #f0f5ff;
}

.grammar-name {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.grammar-desc {
  font-size: 12px;
  color: #666;
}

.sentence-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sentence-item {
  padding: 10px;
  background: #fff;
  border-radius: 4px;
}

.sentence-english {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.sentence-chinese {
  font-size: 13px;
  color: #666;
}

.unit-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 抽屉样式 */
.word-detail, .grammar-detail {
  padding: 20px;
}

.word-header, .grammar-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.word-header h2 {
  margin: 0 0 8px;
  font-size: 28px;
  color: #333;
}

.word-header .phonetic {
  font-size: 16px;
  color: #999;
  margin-right: 12px;
}

.word-header .part-of-speech {
  font-size: 14px;
  color: #667eea;
  background: #f0f5ff;
  padding: 4px 10px;
  border-radius: 4px;
}

.word-detail h4, .grammar-detail h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #333;
}

.word-detail p, .grammar-detail p {
  margin: 0 0 16px;
  color: #666;
  line-height: 1.8;
}

.grammar-detail pre {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}

.example-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.example-english {
  margin: 0 0 8px;
  font-weight: 600;
  color: #333;
}

.example-chinese {
  margin: 0;
  color: #666;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 4px 12px;
  background: #f0f5ff;
  color: #667eea;
  border-radius: 16px;
  font-size: 13px;
}

.all-vocabulary {
  padding: 0 20px;
}

.vocab-search input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e8e8e8;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 16px;
}

.vocab-search input:focus {
  outline: none;
  border-color: #667eea;
}

.vocab-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 20px;
}

.letter-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e8e8e8;
  background: #fff;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.letter-btn:hover {
  border-color: #667eea;
}

.letter-btn.active {
  background: #667eea;
  color: #fff;
  border-color: #667eea;
}

.vocab-list {
  max-height: 60vh;
  overflow-y: auto;
}

.vocab-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.vocab-item:hover {
  background: #f0f5ff;
}

.vocab-item .word {
  min-width: 100px;
  font-weight: 600;
  color: #333;
}

.vocab-item .phonetic {
  min-width: 80px;
  font-size: 12px;
  color: #999;
}

.vocab-item .part {
  font-size: 11px;
  color: #667eea;
  background: #f0f5ff;
  padding: 2px 6px;
  border-radius: 3px;
}

.vocab-item .meaning {
  flex: 1;
  color: #666;
  font-size: 13px;
}
</style>
