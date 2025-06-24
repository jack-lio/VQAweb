<template>
  <div class="selector-area right">
    <select v-model="selectedCode" class="custom-select">
      <option v-for="opt in modelOptions" :key="opt.code" :value="opt.code">
        {{ opt.label }}
      </option>
    </select>
    <div class="d-image">
      <img :src="currentModel.src" alt="Selected Model" class="preview-image" />
        
    </div>
    <div class="instruction-card">
  <h3>Instructions</h3>
  <ol>
    <li>Please select the image and data you want on the left</li>
    <li>Select the prediction model you want</li>
    <li>Click the paper airplane icon in the lower right corner to submit the query</li>
  </ol>
</div>
  </div>
</template>

<script>
export default {
  name: "PictureInput2",
  emits: ['update:selectedModelInfo'],
  data() {
    return {
      modelOptions: [
        { label: "Chiayi", src: "/map_b.png", code: "A" },
        { label: "Keelung", src: "/map_a.png", code: "B" },
        { label: "Udyogamandal", src: "/map_c.png", code: "C" },
        { label: "Kariavattom", src: "/map_d.png", code: "D" },
        { label: "global", src: "/map_e.png", code: "E" }
      ],
      selectedCode: "A"   // << 預設 A
    };
  },
  computed: {
    currentModel() {
      // 找出目前選到的 model option
      return this.modelOptions.find(m => m.code === this.selectedCode) || this.modelOptions[0];
    }
  },
  mounted() {
    this.emitCurrent();
  },
  watch: {
    selectedCode() {
      this.emitCurrent();
    }
  },
  methods: {
    emitCurrent() {
      this.$emit('update:selectedModelInfo', { ...this.currentModel });
    }
  }
};
</script>

<style scoped>
.selector-area {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  padding: 20px;
  margin-top: 0;
  padding-top: 0;
  margin-right: 40px;
  max-width: 500px;
}
.custom-select {
  width: 300px;
  height: 48px;
  font-size: 18px;
  padding-left: 12px;
  border-radius: 8px;
  border: 1px solid #87ceeb;
  background-color: #f0f8ff;
  color: #333;
  margin-bottom: 12px;
}
.custom-select:hover,
.custom-select:focus {
  border-color: #559db3;
}
.d-image {
    position: relative; /* 新增這行讓 .corner-note 可以定位在裡面 */
  margin-bottom: 20px;
}
.preview-image {
  width: 80%;
  max-width: 480px;
    min-width: 480px;
  aspect-ratio: 4 / 3;
  height: 300px;
  object-fit: cover;
  border-radius: 18px;
  border: 1.5px solid #ccc;
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
</style>