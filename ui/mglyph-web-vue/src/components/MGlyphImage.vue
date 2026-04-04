<template>
  <v-skeleton-loader :loading="isLoading" loading-text="Loading image..." type="image">
    <img :src="images[images.length - 1]"></img>
  </v-skeleton-loader>
</template>

<script setup lang="ts">
import type { UUID } from 'crypto'
import { mglyphClient } from '@/clients/mglyph_client'
import { authStore } from '@/main'
import { ref } from 'vue'
import JSZip from 'jszip'

interface Props {
  file_id: UUID
}

const props = defineProps<Props>()
const isLoading = ref(true)
const images = ref<string[]>([])

async function fetchZipFile(fileId: UUID) {
  return await mglyphClient.get(`/file/${fileId}`, {
    authorizeEndpoint: authStore.user ? true : false,
    responseType: 'arraybuffer',
  })
}

async function fetchPreviewImage() {
  isLoading.value = true
  try {
    const response = await fetchZipFile(props.file_id)
    const zip = new JSZip()
    const zipFileContent = await zip.loadAsync(response.data)

    for (const [relativePath, fileEntry] of Object.entries(zipFileContent.files)) {
      // only files
      if (!fileEntry.dir) {
        // read metadata
        if (relativePath === 'metadata.json') {
          // load as blob
          const fileBlob = await fileEntry.async('blob')

          const reader = new FileReader()
          reader.readAsText(fileBlob)

          reader.onload = () => {
            // this.metadata = JSON.parse(reader.result);
            // this.name = this.metadata.name;
            // this.shortName = this.metadata.short_name;
            // this.author = this.metadata.author;
            // this.imageList = this.metadata.images;
            // this.version = this.metadata.version;

            // this.glyphVals = this.imageList.map(glyphInfo => glyphInfo[1])

            // this.info = {
            //     "name":this.name,
            //     "author":this.author,
            //     "version":this.version
            // }

            var metadata = JSON.parse(reader.result as string)
            console.log(metadata)
            var imageList = metadata.images
            var glyphVals = imageList.map((glyphInfo: any) => glyphInfo[1])
          }
        } else if (
          relativePath.endsWith('.png') ||
          relativePath.endsWith('.jpg') ||
          relativePath.endsWith('.jpeg')
        ) {
          // load as blob
          const fileBlob = await fileEntry.async('blob')

          const reader = new FileReader()
          reader.readAsDataURL(fileBlob)

          reader.onload = () => {
            images.value.push(reader.result as string)
          }
        }
      }
    }
  } catch (error) {
    console.error('Error fetching preview image:', error)
  }
  finally {
    isLoading.value = false
  }
}

fetchPreviewImage()
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
