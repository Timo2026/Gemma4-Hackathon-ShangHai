import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

export const useToolStore = defineStore('tools', () => {
  const catalog = ref([])
  const loading = ref(false)

  async function fetchCatalog() {
    loading.value = true
    try {
      const res = await request.get('/tools/catalog')
      catalog.value = res?.data?.catalog || []
    } finally {
      loading.value = false
    }
    return catalog.value
  }

  async function orchestrate(data) {
    const res = await request.post('/tools/orchestrate', data)
    return res
  }

  return { catalog, loading, fetchCatalog, orchestrate }
})
