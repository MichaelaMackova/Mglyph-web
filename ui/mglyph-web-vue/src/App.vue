<template>
  <Header></Header>

  <RouterView />
  <PopupContainer />
</template>

<script setup lang="ts">
import Header from '@/components/Header.vue'
import PopupContainer from '@/components/PopupContainer.vue'
</script>

<style lang="css">
* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  font-family: Arial, Helvetica, sans-serif;
  background-color: var(--md-sys-color-background, #fff8f4);
  color: var(--md-sys-color-on-background, #201b13);
}

a:link {
  color: var(--md-extended-color-hyperlink-color, #041a8f);
}

a:visited {
  color: var(--md-extended-color-hyperlink-visited-color, #830570);
}

.main-padding {
  padding: 0 30px;
}

.main-top-margin {
  margin-top: 20px;
}

.main-bottom-margin {
  margin-bottom: 20px;
}
</style>
