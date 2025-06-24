<template>
  <div class="selector-area">
    <!-- 圖片選擇 -->
    <h2>Image Selection</h2>
    <select v-model="selectedImage" @change="updateFormValues">
      <option v-for="img in imageOptions" :key="img.label" :value="img.src">
        {{ img.label }}
      </option>
    </select>
    <img :src="selectedImage" alt="Selected Image" class="preview-image" />

    <!-- 自動填入的環境數據表格 -->
    <div class="form-area">
      <div class="form-row" v-for="(value, key) in formValues" :key="key">
        <label :for="key">{{ key }}:</label>
        <input :id="key" v-model="formValues[key]" readonly />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PictureInput3",
  data() {
    return {
      // 圖片下拉選單
      imageOptions: [
        { label: "A Image", src: "/a.jpg" },
        { label: "B Image", src: "/b.jpg" },
        { label: "C Image", src: "/c.jpg" }
      ],
      // 當前選擇圖片
      selectedImage: "/a.jpg",

      // 對應各圖片的環境資料
      imageMeta: {
        "/a.jpg": {
          "RH (%)": 80,
          "Rainfall (mm)": 0.5,
          "Temperature (°C)": 28,
          "Wind Direction (°)": 180,
          "Wind Speed (m/s)": 3.2
        },
        "/b.jpg": {
          "RH (%)": 65,
          "Rainfall (mm)": 0,
          "Temperature (°C)": 31,
          "Wind Direction (°)": 90,
          "Wind Speed (m/s)": 1.8
        },
        "/c.jpg": {
          "RH (%)": 72,
          "Rainfall (mm)": 1.2,
          "Temperature (°C)": 26,
          "Wind Direction (°)": 135,
          "Wind Speed (m/s)": 2.4
        },
        "/d.jpg": {
          "RH (%)": 72,
          "Rainfall (mm)": 1.2,
          "Temperature (°C)": 26,
          "Wind Direction (°)": 135,
          "Wind Speed (m/s)": 2.4
        }
      },

      // 表格內容（隨圖片變動）
      formValues: {}
    };
  },
  mounted() {
    this.updateFormValues(); // 初始化表格值
  },
  methods: {
    updateFormValues() {
      this.formValues = { ...this.imageMeta[this.selectedImage] };
    }
  }
};
</script>

<style scoped>
.selector-area {
  padding: 20px;
  max-width: 350px;
  background-color: #f9f9f9;
  border-radius: 10px;
}
.preview-image {
  width: 100%;
  margin-top: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
}
.form-area {
  margin-top: 20px;
  padding: 10px;
  border: 1px solid #a5d2ff;
  background-color: #eaf6ff;
  border-radius: 8px;
}
.form-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
label {
  font-weight: bold;
  margin-right: 10px;
}
input {
  width: 100px;
  text-align: right;
}
</style>
