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
  background-color: rgb(var(--md-sys-color-background, 255, 248, 244));
  color: rgb(var(--md-sys-color-on-background, 32, 27, 19));
}

a:link {
  color: rgb(var(--md-extended-color-hyperlink-color, 4, 26, 143));
}

a:visited {
  color: rgb(var(--md-extended-color-hyperlink-visited-color, 131, 5, 112));
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
