<template>
  <div id="nav">
    <RouterLink to="/">Home</RouterLink>
    <!-- Better way -->
    <RouterLink :to="{ name: 'Clicker' }">Clicker</RouterLink>
  </div>

  <button @click="toggleTheme">Toggle Theme</button>

  <RouterView />
</template>

<script setup lang="ts">
  function toggleTheme() {
    const htmlElement = document.documentElement
    htmlElement.classList.toggle('dark-theme')
    // Save preference to localStorage
    if (htmlElement.classList.contains('dark-theme')) {
      localStorage.setItem('theme-preference', 'dark')
    } else {
      localStorage.setItem('theme-preference', 'light') 
    }
  }

  function fetchTheme() {
    const htmlElement = document.documentElement
    const currentTheme = localStorage.getItem('theme-preference')
    if (currentTheme === 'dark') {
      htmlElement.classList.add('dark-theme')
    } else if (currentTheme === 'light') {
      htmlElement.classList.remove('dark-theme')
    } else {
      // If no preference is set, use system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (prefersDark) {
        htmlElement.classList.add('dark-theme')
      } else {
        htmlElement.classList.remove('dark-theme')
      }
    }
  }

  import { onMounted } from 'vue'
  
  onMounted(() => {
    fetchTheme()
  })
</script>

<style lang="css">
  html, body {
    background-color: var(--md-sys-color-background);
    color: var(--md-sys-color-on-background);
  }

  a:link {
    color: var(--md-extended-color-hyperlink-color);
  }

  a:visited {
    color: var(--md-extended-color-hyperlink-visited-color);
  }
</style>
