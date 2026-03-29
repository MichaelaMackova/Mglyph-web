<template>
  <div v-show="isVisible" class="popup-note" :class="props.type">
    <div class="popup-type">{{ props.type?.toUpperCase() }}</div>
    <div class="popup-message">{{ props.message }}</div>
    <i v-if="props.closable" class="fa-solid fa-xmark" @click="closePopup"></i>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  message: string
  type?: 'info' | 'warning' | 'error'
  closable?: boolean
  closeCallback?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  message: '',
  type: 'info',
  closable: true,
  closeCallback: () => {},
})

function closePopup() {
  isVisible.value = false
  props.closeCallback()
}

const isVisible = ref<boolean>(true)
</script>

<style lang="css" scoped>
.popup-note {
  position: relative;
  border-radius: 5px;
  color: white;
  pointer-events: auto;
  overflow: clip;
  width: 300px;

  &.info {
    background-color: #2196f3;
  }

  &.error {
    background-color: #f44336;
  }

  &.warning {
    background-color: #ff9800;
  }

  > i {
    position: absolute;
    top: 5px;
    right: 5px;
    cursor: pointer;
  }

  .popup-type {
    font-weight: bold;
    padding: 10px 20px 5px 20px;
    font-size: 0.8em;
    opacity: 0.8;
  }

  .popup-message {
    padding: 10px 20px 15px 20px;
    background-color: rgba(255, 255, 255, 0.2);
  }
}
</style>
