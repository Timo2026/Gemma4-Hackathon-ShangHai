import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

export const useIPStore = defineStore('ip', () => {
  const profiles = ref([])
  const cases = ref([])
  const materials = ref([])
  const trustTypes = ref([])

  async function fetchPlatforms() {
    const res = await request.get('/ip/platforms')
    return res?.data?.platforms || []
  }

  async function createProfile(data) {
    return await request.post('/ip/profile', data)
  }

  async function createCase(data) {
    return await request.post('/ip/case', data)
  }

  async function uploadMaterial(data) {
    return await request.post('/ip/material', data)
  }

  async function fetchMaterials() {
    const res = await request.get('/ip/materials')
    materials.value = res?.data?.items || []
    return materials.value
  }

  async function fetchTrustTypes() {
    const res = await request.get('/ip/trust-types')
    trustTypes.value = res?.data?.types || []
    return trustTypes.value
  }

  async function generateTrustContent(data) {
    return await request.post('/ip/trust-content', data)
  }

  async function generateStrategy(data) {
    return await request.post('/ip/strategy', data)
  }

  return {
    profiles, cases, materials, trustTypes,
    fetchPlatforms, createProfile, createCase,
    uploadMaterial, fetchMaterials, fetchTrustTypes,
    generateTrustContent, generateStrategy,
  }
})
