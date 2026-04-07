<template>
  <MGlyphImage :isLoading="isLoading" :imageSrc="imageSrc" />
</template>

<script setup lang="ts">
import type { UUID } from 'crypto'
import { fetchZipFileAsArrayBuffer, unzip } from '@/services/zip-file-utils'
import MGlyphImage from '@/components/MGlyphImage.vue'
import { ref } from 'vue'
interface Props {
  file_id: UUID
}

const props = defineProps<Props>()
const isLoading = ref(true)
const imageSrc = ref<string | null>(null)

async function fetchPreviewImage() {
  isLoading.value = true
  try {
    const response = await fetchZipFileAsArrayBuffer(props.file_id)
    const zipFileContent = await unzip(response.data)
    imageSrc.value = zipFileContent.images[(zipFileContent.images.length > 20) ? (zipFileContent.images.length - 10) : (zipFileContent.images.length - 1)].blobUrl

  } catch (error) {
    console.error('Error fetching preview image:', error)
  }
  finally {
    isLoading.value = false
  }
}

fetchPreviewImage()
</script>
