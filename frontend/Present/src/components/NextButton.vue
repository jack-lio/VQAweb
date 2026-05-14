<template>
  <button
    class="next-button"
    type="button"
    :style="buttonStyle"
    @click="onNextButtonContainerClick"
  >
    Next
  </button>
</template>

<script lang="ts">
import { defineComponent, type PropType } from "vue";

export default defineComponent({
  name: "NextButton",
  props: {
    property1: {
      type: String,
      default: "",
    },
    nextButtonPosition: {
      type: String,
      default: "relative",
    },
    nextButtonTop: {
      type: String,
      default: "unset",
    },
    nextButtonLeft: {
      type: String,
      default: "unset",
    },
    onNextButtonContainerClick: {
      type: Function as PropType<() => void>,
      default: () => undefined,
    },
  },
  computed: {
    buttonStyle() {
      return {
        position: this.nextButtonPosition,
        top: this.nextButtonTop,
        left: this.nextButtonLeft,
      };
    },
  },
});
</script>

<style scoped>
.next-button {
  border: 0;
  border-radius: 8px;
  background: #2563eb;
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  min-height: 48px;
  padding: 0 24px;
}
</style>
