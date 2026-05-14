<template>
  <h1 class="main-title">Federated Multimodal Air Quality Prediction</h1>

  <div class="main-row">
    <PictureInput v-model:selectedImageInfo="selectedImageInfo" />
    <PictureInput2 v-model:selectedModelInfo="selectedModelInfo" />
  </div>

  <button
    class="send-btn-svg"
    @click="sendToBackend"
    :disabled="isLoading"
    aria-label="Send"
  >
    <img src="/send.svg" alt="Send" class="send-icon" />
  </button>

  <div v-if="isLoading" class="result-popup">
    <img src="/loading.gif" alt="Loading..." class="loading-icon" /><br />
    AI model is predicting, please wait...
  </div>

  <div v-else-if="resultVisible && result" class="result-popup">
    <h3>Prediction results</h3>
    <div>AQI Status: <b>{{ result.AQI }}</b></div>
    <div>Description: {{ result.description }}</div>
  </div>

  <div v-else-if="errorMsg" class="result-popup error">{{ errorMsg }}</div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import PictureInput from '../components/PictureInput.vue'
import PictureInput2 from '../components/PictureInput2.vue'

const selectedImageInfo = ref({})
const selectedModelInfo = ref({})
const isLoading = ref(false)
const result = ref(null)
const errorMsg = ref('')
const resultVisible = ref(false)

async function sendToBackend() {
  if (resultVisible.value) {
    resultVisible.value = false
    result.value = null
    errorMsg.value = ''
    return
  }

  if (!selectedImageInfo.value.src && !selectedImageInfo.value.file) {
    errorMsg.value = 'Please select or upload an image.'
    return
  }

  isLoading.value = true
  result.value = null
  errorMsg.value = ''
  resultVisible.value = false

  const formData = new FormData()
  formData.append('image', await getImageFile(selectedImageInfo.value))
  formData.append('rh', selectedImageInfo.value.meta?.['RH (%)'] ?? '')
  formData.append('rainfall', selectedImageInfo.value.meta?.['Rainfall (mm)'] ?? '')
  formData.append('temperature', selectedImageInfo.value.meta?.['Temperature (C)'] ?? '')
  formData.append('wd_hr', selectedImageInfo.value.meta?.['Wind Direction (deg)'] ?? '')
  formData.append('ws_hr', selectedImageInfo.value.meta?.['Wind Speed (m/s)'] ?? '')
  formData.append('model_name', selectedModelInfo.value.code ?? 'A')

  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    const res = await axios.post('/api/predict', formData)

    if (res.data.error) {
      errorMsg.value = res.data.error
    } else {
      result.value = res.data
    }
    resultVisible.value = true
  } catch (err) {
    errorMsg.value = 'Server error, please retry'
    resultVisible.value = true
  } finally {
    isLoading.value = false
  }
}

async function getImageFile(imageInfo) {
  if (imageInfo.file) {
    return imageInfo.file
  }

  const response = await fetch(imageInfo.src)
  const blob = await response.blob()
  const filename = `${imageInfo.label || 'image'}.jpg`
  return new File([blob], filename, { type: blob.type })
}
</script>

<style scoped>
.main-title {
  text-align: center;
  margin-top: 10px;
  font-size: 2.4rem;
  font-weight: bold;
  background: linear-gradient(90deg, #3751d7 40%, #9f5afd 60%, #53d7d1 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 2px 2px 16px #dbeafe, 0 4px 8px #3751d744;
  word-break: break-word;
  white-space: normal;
}

.main-row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: flex-start;
  gap: 80px;
  max-width: 1100px;
  margin: 0 auto;
  padding-top: 0;
  padding-bottom: 80px;
}

.send-btn-svg {
  position: fixed;
  right: 56px;
  bottom: 24px;
  width: 72px;
  height: 72px;
  background: none;
  border: none;
  cursor: pointer;
  z-index: 999;
  transition: transform 0.2s;
}

.send-btn-svg:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn-svg:hover:enabled {
  transform: scale(1.1) rotate(-10deg);
}

.send-icon {
  width: 56px;
  height: 56px;
}

.loading-icon {
  width: 54px;
}

.result-popup {
  position: fixed;
  right: 140px;
  bottom: 60px;
  min-width: 380px;
  max-width: 520px;
  background: #ffe6e6;
  color: #1a1a2f;
  border-radius: 22px;
  padding: 24px 28px 20px;
  box-shadow: 0 6px 32px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.08);
  border: 2.5px solid #efc5c5;
  z-index: 999;
  text-align: left;
  font-size: 1.5rem;
  line-height: 1.6;
}

.result-popup h3 {
  margin-top: 0;
  font-size: 1.8rem;
  font-weight: 900;
  letter-spacing: 1.2px;
  color: #2a1a2f;
}

.result-popup.error {
  color: #d53a3a;
  background: #ffe6e6;
  font-weight: bold;
  border-color: #e99898;
}
</style>
