<template>
     <h1 class="main-title">
      Federated Multimodal Air Quality Prediction
  </h1>
  <div class="main-row">
    <PictureInput v-model:selectedImageInfo="selectedImageInfo" />
    <PictureInput2 v-model:selectedModelInfo="selectedModelInfo" />
  </div>

  <!-- 固定右下角 send 按鈕 -->
  <button
    class="send-btn-svg"
    @click="sendToBackend"
    :disabled="isLoading"
    aria-label="Send"
  >
    <img src="/send.svg" alt="Send" style="width:56px;height:56px;" />
  </button>

  <!-- 右下角浮出 Loading -->
  <div v-if="isLoading" class="result-popup">
    <img src="/loading.gif" alt="Loading..." style="width:54px" /><br />
    AI model is predicting, please wait...
  </div>

  <!-- 右下角浮出 預測結果 -->
  <div v-else-if="resultVisible && result" class="result-popup">
    <h3>Prediction results</h3>
    <div>AQI Status:：<b>{{ result.AQI }}</b></div>
    <div>Description: {{ result.description }}</div>
  </div>

  <!-- 右下角浮出 錯誤訊息 -->
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
const resultVisible = ref(false) // 決定結果框是否顯示

async function sendToBackend() {
  // 如果已經顯示結果，這次點擊就是「收起」
  if (resultVisible.value) {
    resultVisible.value = false
    result.value = null
    errorMsg.value = ''
    return
  }
  // 否則，送API、顯示loading
  isLoading.value = true
  result.value = null
  errorMsg.value = ''
  resultVisible.value = false

  // 表單準備
  const formData = new FormData()
  formData.append(
    'image',
    await urlToFile(
      selectedImageInfo.value.src,
      (selectedImageInfo.value.label || 'image') + '.jpg'
    )
  )
  formData.append('rh', selectedImageInfo.value.meta?.['RH (%)'] ?? '')
  formData.append('rainfall', selectedImageInfo.value.meta?.['Rainfall (mm)'] ?? '')
  formData.append('temperature', selectedImageInfo.value.meta?.['Temperature (°C)'] ?? '')
  formData.append('wd_hr', selectedImageInfo.value.meta?.['Wind Direction (°)'] ?? '')
  formData.append('ws_hr', selectedImageInfo.value.meta?.['Wind Speed (m/s)'] ?? '')
  formData.append('model_name', selectedModelInfo.value.code ?? 'A')


  try {
    // 模擬 1 秒 loading（如只要等 API 請移除）
    await new Promise(resolve => setTimeout(resolve, 2000))
    // await new Promise(r => setTimeout(r, 1000))
    const res = await axios.post('/api/predict', formData)
    if (res.data.error) {
      errorMsg.value = res.data.error
      resultVisible.value = true
    } else {
      result.value = res.data
      resultVisible.value = true
    }
  } catch (err) {
    errorMsg.value = 'Server error, please retry'
    resultVisible.value = true
  }
  isLoading.value = false
}

// 工具：圖片路徑轉 file
async function urlToFile(url, filename) {
  const res = await fetch(url)
  const blob = await res.blob()
  return new File([blob], filename, { type: blob.type })
}
// 工具：A Model → "A"
function modelLabelToKey(label) {
  return label?.[0]?.toUpperCase() || 'A'
}
</script>

<style scoped>
.main-title {
  text-align: center;
  margin-top: 10px;
  font-size: rem;
  font-weight: bold;
  background: linear-gradient(90deg, #3751d7 40%, #9f5afd 60%, #53d7d1 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 2px 2px 16px #dbeafe, 0 4px 8px #3751d744;
  letter-spacing: 1.5px;
  /* 這兩行讓長標題自動換行 */
  word-break: break-word;
  white-space: normal;
}

.main-row {
    display: flex;
  flex-direction: row;
  justify-content: center;     /* 讓左右元素集中 */
  align-items: flex-start;
  gap: 80px;                   /* 控制兩個元件間距，可再調小一點 */
  max-width: 1100px;           /* 最多1200px（你可以依實際需要調） */
  margin: 0 auto;              /* 水平置中 */
  padding-top: 0;   /* 這裡設 0 */
  margin-top: 0; 
   padding-bottom: 80px;   /* 如果有的話 */
}
/* 右下角按鈕樣式 */
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
/* 右下角結果浮出 */
.result-popup {
  position: fixed;
 right: 140px;
  bottom: 60px;
  min-width: 380px;
  max-width: 520px;
  background: #ffe6e6;
  color: #1a1a2f;
  border-radius: 22px;
  padding: 24px 28px 20px 28px;
  box-shadow: 0 6px 32px 0 rgba(0,0,0,0.10), 0 2px 4px 0 rgba(0,0,0,0.08);
  border: 2.5px solid #efc5c5;
  z-index: 999;
  text-align: left;
  font-size: 1.5rem; /* ✅ 字體變小 */
  line-height: 1.6; 
}
.result-popup h3 {
  margin-top: 0;
  font-size: 1.8rem;  /* 原本是 2.3rem */
  font-weight: 900;
  letter-spacing: 1.2px;
  color: #2a1a2f;
}
body {
  background: #fff;
  margin: 0;
  padding: 0;
  
}

#app {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 24px;     /* 或 32px，視你設計 */
}
.result-popup.error {
  color: #d53a3a;
  background: #ffe6e6;
  font-weight: bold;
  border-color: #e99898;
}
</style>