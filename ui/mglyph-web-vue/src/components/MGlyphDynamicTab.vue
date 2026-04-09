<template>
  <div class="tab-container">
    <div class="mglyph-container">
      <div class="mglyph-image-container">
        <MGlyphImage
          :isLoading="isLoadingZip"
          :imageSrc="zipFileContent?.images[glyphIndex]?.blobUrl || null"
        />
      </div>
      <div class="mglyph-value">
        {{
          isLoadingZip || zipFileContent?.images[glyphIndex]?.glyphValue === undefined
            ? 'x'
            : zipFileContent.images[glyphIndex]!.glyphValue
        }}
      </div>
    </div>
    <v-slider
      v-model="glyphIndex"
      :max="(zipFileContent?.images.length || 0) - 1"
      :min="0"
      :step="1"
      :thumb-label="false"
      hide-details
    >
      <template v-slot:prepend>
        {{ zipFileContent?.images[0]?.glyphValue || 0 }}
      </template>
      <template v-slot:append>
        {{ zipFileContent?.images[(zipFileContent?.images.length || 0) - 1]?.glyphValue || 0 }}
      </template>
      <template v-slot:thumb-label="{ modelValue }">
        {{ zipFileContent?.images[modelValue]?.glyphValue || 0 }}
      </template>
    </v-slider>
  </div>
</template>

<script setup lang="ts">
import { type ZipFileContent } from '@/services/zip-file-utils'
import MGlyphImage from '@/components/MGlyphImage.vue'
import { ref } from 'vue'

interface Props {
  zipFileContent: ZipFileContent | null
  isLoadingZip: boolean
}

const props = withDefaults(defineProps<Props>(), {
  zipFileContent: null,
  isLoadingZip: true,
})

const glyphIndex = ref(0)
</script>

<style lang="css" scoped>
.tab-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 50vw;
  margin: 0 auto;
}

.mglyph-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  width: 50%;

  & .mglyph-image-container {
    width: 100%;
    aspect-ratio: 1/1;
  }

  & .mglyph-value {
    font-size: 120%;
  }
}

.v-slider {
  width: 100%;
  --v-theme-surface-variant: var(--md-sys-color-on-surface, 32, 27, 19);
  --v-theme-on-surface-variant: var(--md-sys-color-surface, 255, 248, 244);
}
</style>
