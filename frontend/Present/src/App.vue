<template>
  <div :style="zoomStyle">
    <router-view />
  </div>
</template>

<script>
export default {
  data() {
    return {
      zoom: 0.8,
    }
  },
  computed: {
    zoomStyle() {
      return {
        transform: `scale(${this.zoom})`,
        transformOrigin: "0 0",
        width: `${100 / this.zoom}%`,
      }
    },
  },
}
</script>
