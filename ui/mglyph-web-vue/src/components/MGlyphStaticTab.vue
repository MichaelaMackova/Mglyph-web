<template>
  <div class="tab-container">
    <div
      class="row-container"
      v-for="(row, rowNum) in [firstRowIndexes, secondRowIndexes, thirdRowIndexes]"
      :key="rowNum"
      v-show="row.length > 0 && (!isLoadingZip || rowNum === 0)"
    >
      <div class="mglyph-container" v-for="(glyphIndex, i) in row" :key="i">
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
              : zipFileContent.images[glyphIndex].glyphValue
          }}
        </div>
      </div>
    </div>
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

const firstRowIndexes = ref<number[]>([-1, -1, -1, -1, -1])
const secondRowIndexes = ref<number[]>([])
const thirdRowIndexes = ref<number[]>([])

function calculateImageIndexes() {
  if (!props.zipFileContent) {
    firstRowIndexes.value = [-1, -1, -1, -1, -1]
    secondRowIndexes.value = []
    thirdRowIndexes.value = []
    return
  }

  const totalImages = props.zipFileContent.images.length
  if (totalImages === 0) {
    firstRowIndexes.value = []
    secondRowIndexes.value = []
    thirdRowIndexes.value = []
    return
  }

  // Calculate indexes for the first row (5 images evenly spaced)
  if (totalImages <= 5) {
    firstRowIndexes.value = Array.from({ length: totalImages }, (_, i) => i)
  } else {
    firstRowIndexes.value = Array.from({ length: 5 }, (_, i) =>
      Math.floor((i * (totalImages - 1)) / 4),
    )

    if (totalImages > 10) {
      // Calculate indexes for the second row (5 images with small differences from beginning)
      const differencePercentage = Math.max(0.01, 1 / (totalImages - 1)) // Ensure unique indexes even for small totalImages
      secondRowIndexes.value = Array.from({ length: 5 }, (_, i) =>
        Math.floor(i * totalImages * differencePercentage),
      )

      // Calculate indexes for the third row (5 images with small differences at the end - ascending order)
      thirdRowIndexes.value = Array.from(
        { length: 5 },
        (_, i) =>
          totalImages -
          1 -
          Math.floor(4 * differencePercentage * totalImages) +
          Math.floor(i * totalImages * differencePercentage),
      )
    }
  }
}

calculateImageIndexes()
</script>

<style lang="css" scoped>
.tab-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  gap: 5px;
}

.row-container {
  display: flex;
  justify-content: center;
  gap: 5px;
  width: 100%;
}

.mglyph-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  width: 15%;
  max-width: 130px;
  min-width: 50px;

  & .mglyph-image-container {
    width: 100%;
    aspect-ratio: 1/1;
  }

  & .mglyph-value {
    font-size: 85%;
  }
}
</style>
