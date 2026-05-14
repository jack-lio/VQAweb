<template>
  <div class="selector-area right">
    <div class="top-controls">
      <button class="switch-btn">Select Model</button>
      <select v-model="selectedCode" class="custom-select">
        <option v-for="opt in modelOptions" :key="opt.code" :value="opt.code">
          {{ opt.label }}
        </option>
      </select>
    </div>

    <div class="d-image">
      <img :src="currentModel.src" alt="Selected Model" class="preview-image" />
    </div>

    <div class="instruction-card">
      <h3>Instructions</h3>
      <ol>
        <li>Please select the image and data you want on the left.</li>
        <li>Select the prediction model you want.</li>
        <li>Click the paper airplane icon in the lower right corner to submit the query.</li>
      </ol>
    </div>
  </div>
</template>

<script>
export default {
  name: "PictureInput2",
  emits: ["update:selectedModelInfo"],
  data() {
    return {
      modelOptions: [
        { label: "Taiwan_model", src: "/taiwan.png", code: "A" },
        { label: "India_model", src: "/ind.png", code: "B" },
        { label: "global_model", src: "/555.png", code: "E" },
      ],
      selectedCode: "A",
    }
  },
  computed: {
    currentModel() {
      return this.modelOptions.find(model => model.code === this.selectedCode) || this.modelOptions[0]
    },
  },
  mounted() {
    this.emitCurrent()
  },
  watch: {
    selectedCode() {
      this.emitCurrent()
    },
  },
  methods: {
    emitCurrent() {
      this.$emit("update:selectedModelInfo", { ...this.currentModel })
    },
  },
}
</script>

<style scoped>
.selector-area {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0;
  margin: 0;
}

.top-controls {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  margin-bottom: 8px;
  margin-top: 0;
  padding: 0;
}

.custom-select {
  width: 220px;
  height: 48px;
  font-size: 18px;
  padding-left: 12px;
  border-radius: 8px;
  border: 1px solid #87ceeb;
  background-color: #f0f8ff;
  color: #333;
}

.custom-select:hover,
.custom-select:focus {
  border-color: #559db3;
}

.d-image {
  max-width: 620px;
  position: relative;
  margin-bottom: 20px;
}

.preview-image {
  width: 100%;
  max-width: 650px;
  min-width: 500px;
  height: 450px;
  object-fit: contain;
  border-radius: 18px;
  border: 1.5px solid #ccc;
  display: block;
  margin: 0 auto;
  background-color: white;
}

.instruction-card {
  background-color: #f9fbff;
  border: 1.5px solid #c0d3e5;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  padding: 18px 22px;
  margin-bottom: 32px;
  width: 400px;
  max-width: 90%;
  font-size: 1.05rem;
  line-height: 1.7;
  color: #333;
  float: right;
  margin-right: 10px;
}

.instruction-card h3 {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 1.4rem;
  color: #1e3a5f;
  font-weight: bold;
}

.instruction-card ol {
  margin: 0;
  padding-left: 24px;
}

.switch-btn {
  height: 48px;
  padding: 0 20px;
  font-size: 18px;
  border-radius: 12px;
  background-color: #f8f8f8;
  border: 1.5px solid #ccc;
  color: #000;
  font-weight: 500;
  cursor: default;
  box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.08);
  transition: background-color 0.2s;
}
</style>
