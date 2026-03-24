<template>
  <div class="main-padding">
    <h1>Home</h1>
    <p>Welcome to the home page!</p>
    <button @click="addPopup">Show Info Popup</button>
  </div>
</template>

<script setup lang="ts">
import { popupStore } from '@/main'
import { ref } from 'vue'

const numberOfPopups = ref<number>(0)

function addPopup() {
  popupStore.addPopup(
    `This is an info popup! ${numberOfPopups.value}`,
    popupStore.PopupTypeEnum.info,
  )

  numberOfPopups.value++
}
</script>
