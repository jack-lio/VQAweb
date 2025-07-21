<template>
  <div :style="zoomStyle">
    <!-- 整個應用內容 -->
    <router-view />
  </div>
</template>

<script>
export default {
  data() {
    return {
      zoom: 0.8  // 這裡改成你想要的比例
    }
  },
  computed: {
    zoomStyle() {
      return {
        transform: `scale(${this.zoom})`,
        transformOrigin: '0 0',
        width: `${100 / this.zoom}%`, // 為了防止捲軸異常
      };
    }
  }
}
</script>
