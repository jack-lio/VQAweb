<template>
  <div class="selector-area">
    <!-- 圖片選擇方式按鈕 -->
    <div class="flex-row">
      <select v-model="selected" class="custom-select" v-if="selectedImageSource === 'select'">
        <option v-for="img in imageOptions" :key="img.label" :value="img">
          {{ img.label }}
        </option>
      </select>
      <button @click="useSelect" :disabled="selectedImageSource === 'select'" class="switch-btn">Select Image</button>
      <button @click="useUpload" :disabled="selectedImageSource === 'upload'" class="switch-btn">Upload</button>

      <!-- ⛳ 自訂 upload button -->
      <div v-if="selectedImageSource === 'upload'" class="upload-wrapper">
        <button @click="$refs.realFileInput.click()" class="switch-btn">Choose File</button>
        <span v-if="uploadFile">{{ uploadFile.name }}</span>
        <input ref="realFileInput" type="file" accept="image/*" @change="onFileChange" style="display: none;" />
      </div>
    </div>

    <!-- 預設圖像與表單 -->
    <div v-if="selectedImageSource === 'select'">
      <div class="d-image">
        <img :src="selected.src" alt="Selected Image" class="preview-image" />
      </div>
      <div class="form-area">
        <div class="form-row" v-for="(value, key) in meta" :key="key">
          <label>{{ key }}:</label>
          <input :value="value" readonly />
        </div>
      </div>
    </div>

    <!-- 上傳圖像與表單 -->
    <div v-else>
      <div class="d-image" v-if="previewUrl">
        <img :src="previewUrl" alt="Upload Preview" class="preview-image" />
      </div>
      <div class="form-area">
        <div class="form-row" v-for="(value, key) in uploadMeta" :key="key">
          <label>{{ key }}:</label>
          <input v-model="uploadMeta[key]" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PictureInput",
  emits: ['update:selectedImageInfo'],
  data() {
    return {
      imageOptions: [
        { label: "Chiayi", src: "/a.jpg" },
        { label: "Keelung", src: "/b.jpg" },
        { label: "Udyogamandal", src: "/c.jpg" },
        { label: "Kariavattom", src: "/d.jpg" }
      ],
      imageMeta: {
        "/a.jpg": { "RH (%)": 80.2, "Rainfall (mm)": 0.5, "Temperature (°C)": 28, "Wind Direction (°)": 180, "Wind Speed (m/s)": 3.2 },
        "/b.jpg": { "RH (%)": 65, "Rainfall (mm)": 0, "Temperature (°C)": 31, "Wind Direction (°)": 90, "Wind Speed (m/s)": 1.8 },
        "/c.jpg": { "RH (%)": 72, "Rainfall (mm)": 1.2, "Temperature (°C)": 26, "Wind Direction (°)": 135, "Wind Speed (m/s)": 2.4 },
        "/d.jpg": { "RH (%)": 60, "Rainfall (mm)": 0.1, "Temperature (°C)": 29, "Wind Direction (°)": 200, "Wind Speed (m/s)": 2.9 }
      },
      selected: { label: "Chiayi", src: "/a.jpg" },
      meta: {},
      selectedImageSource: 'select',   // 'select' or 'upload'
      uploadFile: null,
      previewUrl: '',
      uploadMeta: { "RH (%)": "", "Rainfall (mm)": "", "Temperature (°C)": "", "Wind Direction (°)": "", "Wind Speed (m/s)": "" }
    }
  },
  mounted() {
    this.meta = { ...this.imageMeta[this.selected.src] }
    this.$emitInfo()
  },
  watch: {
    selected: {
      handler(val) {
        if (this.selectedImageSource !== 'select' || !val) return;
        this.meta = { ...this.imageMeta[val.src] }
        this.$emitInfo()
      }
    },
    uploadMeta: {
      handler() {
        if (this.selectedImageSource === 'upload') this.$emitInfo()
      },
      deep: true
    }
  },
  methods: {
    useSelect() {
      this.selectedImageSource = 'select'
      this.$emitInfo()
    },
    useUpload() {
      this.selectedImageSource = 'upload'
      this.uploadFile = null
      this.previewUrl = ''
      this.uploadMeta = { "RH (%)": "", "Rainfall (mm)": "", "Temperature (°C)": "", "Wind Direction (°)": "", "Wind Speed (m/s)": "" }
      this.$emitInfo()
    },
    onFileChange(e) {
      const file = e.target.files[0]
      if (file) {
        this.uploadFile = file
        this.previewUrl = URL.createObjectURL(file)
        this.$emitInfo()
      }
    },
    $emitInfo() {
      if (this.selectedImageSource === 'select') {
        this.$emit('update:selectedImageInfo', {
          label: this.selected.label,
          src: this.selected.src,
          meta: { ...this.meta },
          source: 'select',
          file: null
        })
      } else {
        this.$emit('update:selectedImageInfo', {
          label: this.uploadFile ? this.uploadFile.name : "",
          src: this.previewUrl,
          meta: { ...this.uploadMeta },
          source: 'upload',
          file: this.uploadFile
        })
      }
    }
  }
}
</script>

<style scoped>
.selector-area {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 0;
  padding-top: 0;
  margin-left: 40px;
  max-width: 500px;
  margin-right: auto;
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;

}
.switch-btn {
  height: 44px;           /* 跟 select 一樣高 */
  font-size: 20px;
  padding: 0 22px;        /* 舒服的左右邊界 */
  border-radius: 8px;
  border: 1.5px solid #bbb;
  background: #fafafa;
  color: #222;
  cursor: pointer;
  transition: background 0.15s;
}
.custom-select {
  width: 160px;           /* 寬度可調整 */
  height: 44px;           /* 跟按鈕一樣高 */
  font-size: 20px;        /* 舒服的小字 */
  border-radius: 8px;
  border: 1.5px solid #87ceeb;
  background-color: #f0f8ff;
  color: #333;
  padding-left: 12px;
}
.custom-select:hover,
.custom-select:focus {
  border-color: #559db3;
}
.d-image {
  margin-bottom: 20px;
}
.preview-image {
  width: 100%;
  max-width: 480px;
  height: 300px;
  object-fit: cover;
  border-radius: 18px;
  border: 1.5px solid #ccc;
}
.form-area {
  background-color: #eaf6ff;
  border: 1.5px solid #87ceeb;
  border-radius: 10px;
  padding: 15px;
  width: 100%;
}
.form-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}
label {
  font-weight: bold;
}
input {
  width: 150px;
  text-align: right;
  padding: 5px;
  border-radius: 5px;
  border: 1px solid #ccc;
}
</style>
