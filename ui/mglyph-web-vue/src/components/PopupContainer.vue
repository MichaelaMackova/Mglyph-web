<template>
  <div class="popup-container">
    <PopupNote
      v-for="(n, index) in popupStore.popups.length"
      :key="popupStore.popups[index].id"
      :message="popupStore.popups[index].message"
      :type="popupStore.popups[index].type"
      :closeCallback="() => popupStore.removePopup(index)"
    />
  </div>
</template>

<script setup lang="ts">
import PopupNote from '@/components/PopupNote.vue'
import { popupStore } from '@/main'
</script>

<style lang="css" scoped>
.popup-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  z-index: 10;
  pointer-events: none;

  max-height: calc(100vh - 120px);
  overflow-y: auto;
}
</style>
