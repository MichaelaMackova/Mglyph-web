<template>
  <v-skeleton-loader :loading="props.isLoading" loading-text="Loading image..." type="image">
    <img :src="props.imageSrc"></img>
  </v-skeleton-loader>
</template>

<script setup lang="ts">
interface Props {
  imageSrc: string | null
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  imageSrc: null,
  isLoading: false
})
</script>

<style lang="css" scoped>
img {
  object-fit: contain;
}

img, .v-skeleton-loader, .v-skeleton-loader::v-deep(.v-skeleton-loader__image) {
  height: 100%;
  width: 100%;
  border-radius: 10%;
  box-shadow: 2px 2px 5px 0 rgba(0, 0, 0, 0.19);
}

.v-skeleton-loader::v-deep(.v-skeleton-loader__image) {
  --v-theme-on-surface: 103, 99, 94;
  --v-border-opacity: 0.4;
  --v-theme-surface: 255, 248, 244, 0.5;
}
</style>
