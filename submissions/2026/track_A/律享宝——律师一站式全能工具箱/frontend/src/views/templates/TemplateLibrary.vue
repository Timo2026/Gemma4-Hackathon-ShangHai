<template>
  <div class="template-library">
    <div class="page-header">
      <h2>📚 法律文书模板库</h2>
      <p class="subtitle">90份标准法律文书模板 · 最高法/司法部2024版 · 在线填写一键生成</p>
    </div>

    <!-- 分类筛选 -->
    <el-card shadow="never" class="filter-card">
      <div class="category-tabs">
        <el-radio-group v-model="activeCategory" @change="onCategoryChange">
          <el-radio-button value="">全部模板</el-radio-button>
          <el-radio-button v-for="cat in tplStore.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </el-radio-button>
        </el-radio-group>
      </div>
      <div class="sub-category-bar" v-if="activeSubCategories.length">
        <el-tag
          v-for="sub in activeSubCategories"
          :key="sub.id"
          :type="activeSubCategory === sub.id ? '' : 'info'"
          :effect="activeSubCategory === sub.id ? 'dark' : 'plain'"
          class="sub-tag"
          @click="onSubCategoryClick(sub.id)"
        >
          {{ sub.name }} ({{ sub.count }})
        </el-tag>
      </div>
      <el-input
        v-model="keyword"
        placeholder="搜索模板名称/场景..."
        clearable
        style="max-width:360px; margin-top:12px"
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #append>
          <el-button @click="onSearch">搜索</el-button>
        </template>
      </el-input>
    </el-card>

    <!-- 模板网格 -->
    <div v-loading="tplStore.loading" class="template-grid">
      <el-empty v-if="tplStore.templateList.length === 0 && !tplStore.loading" description="暂无匹配模板" />
      <el-card
        v-for="tpl in tplStore.templateList"
        :key="tpl.id"
        shadow="hover"
        class="template-card"
        @click="goFill(tpl.id)"
      >
        <div class="tpl-icon">{{ getCategoryIcon(tpl.category) }}</div>
        <div class="tpl-info">
          <h3 class="tpl-name">{{ tpl.name }}</h3>
          <p class="tpl-scene">{{ tpl.scene }}</p>
          <div class="tpl-meta">
            <el-tag size="small" type="info">{{ tpl.source }}</el-tag>
            <el-tag size="small" :type="getCategoryType(tpl.category)">{{ getCategoryLabel(tpl.category) }}</el-tag>
          </div>
        </div>
        <el-icon class="tpl-arrow"><ArrowRight /></el-icon>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTemplateStore } from '@/stores/templates'

const router = useRouter()
const tplStore = useTemplateStore()

const activeCategory = ref('')
const activeSubCategory = ref('')
const keyword = ref('')

const activeSubCategories = computed(() => {
  if (!activeCategory.value) return []
  const cat = tplStore.categories.find(c => c.id === activeCategory.value)
  return cat?.sub_categories || []
})

function onCategoryChange(val) {
  activeSubCategory.value = ''
  onSearch()
}

function onSubCategoryClick(subId) {
  activeSubCategory.value = activeSubCategory.value === subId ? '' : subId
  onSearch()
}

function onSearch() {
  tplStore.fetchTemplates({
    category: activeCategory.value || undefined,
    sub_category: activeSubCategory.value || undefined,
    keyword: keyword.value || undefined,
  })
}

function goFill(templateId) {
  router.push(`/templates/${templateId}/fill`)
}

function getCategoryIcon(cat) {
  const icons = { civil: '⚖️', legal_aid: '🆘', lawyer: '👨‍⚖️' }
  return icons[cat] || '📄'
}

function getCategoryType(cat) {
  const types = { civil: '', legal_aid: 'success', lawyer: 'warning' }
  return types[cat] || 'info'
}

function getCategoryLabel(cat) {
  const labels = { civil: '民事诉讼', legal_aid: '法律援助', lawyer: '律师辅助' }
  return labels[cat] || cat
}

onMounted(() => {
  tplStore.fetchCategories()
  tplStore.fetchTemplates()
})
</script>

<style scoped>
.template-library {
  max-width: 1400px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 24px;
}
.page-header h2 {
  font-size: 22px;
  font-weight: 600;
}
.subtitle {
  color: #999;
  font-size: 14px;
  margin-top: 4px;
}
.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}
.category-tabs {
  margin-bottom: 12px;
}
.sub-category-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}
.sub-tag {
  cursor: pointer;
}
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
  min-height: 200px;
}
.template-card {
  cursor: pointer;
  border-radius: 12px;
  transition: transform 0.2s;
}
.template-card:hover {
  transform: translateY(-2px);
}
.template-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}
.tpl-icon {
  font-size: 36px;
  flex-shrink: 0;
}
.tpl-info {
  flex: 1;
  min-width: 0;
}
.tpl-name {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tpl-scene {
  font-size: 13px;
  color: #999;
  margin: 0 0 8px;
}
.tpl-meta {
  display: flex;
  gap: 6px;
}
.tpl-arrow {
  color: #c0c4cc;
  font-size: 18px;
  flex-shrink: 0;
}
</style>
