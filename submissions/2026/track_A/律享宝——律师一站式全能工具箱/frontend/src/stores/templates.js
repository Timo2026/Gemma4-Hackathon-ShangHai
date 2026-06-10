import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

export const useTemplateStore = defineStore('templates', () => {
  const categories = ref([])
  const templateList = ref([])
  const currentTemplate = ref(null)
  const loading = ref(false)

  async function fetchCategories() {
    const res = await request.get('/templates/categories')
    categories.value = res?.data?.categories || []
    return res
  }

  async function fetchTemplates(params = {}) {
    loading.value = true
    try {
      const query = {}
      if (params.category) query.category = params.category
      if (params.sub_category) query.sub_category = params.sub_category
      if (params.keyword) query.keyword = params.keyword
      const res = await request.get('/templates', { params: query })
      templateList.value = res?.data?.items || []
      return res
    } finally {
      loading.value = false
    }
  }

  async function fetchTemplateDetail(templateId) {
    loading.value = true
    try {
      const res = await request.get(`/templates/${templateId}`)
      currentTemplate.value = res?.data || null
      return res?.data
    } finally {
      loading.value = false
    }
  }

  async function renderTemplate(templateId, formData) {
    const res = await request.post('/templates/render', {
      template_id: templateId,
      form_data: formData,
    })
    return res?.data
  }

  return {
    categories, templateList, currentTemplate, loading,
    fetchCategories, fetchTemplates, fetchTemplateDetail, renderTemplate,
  }
})
