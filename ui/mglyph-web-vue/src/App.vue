<template>
  <div id="nav">
    <RouterLink to="/">Home</RouterLink>
    <!-- Better way -->
    <RouterLink :to="{ name: 'Clicker' }">Clicker</RouterLink>
  </div>

  <RouterView />
</template>
