<template>
  <div class="sort-container" :class="isAnimating ? 'animated' : ''">
    <div class="glyphs-container">
      <div class="glyph-image-container">
        <MGlyphImage :imageSrc="props.mglyph1Src" :showShadow="false" />
      </div>

      <div class="glyph-image-container">
        <MGlyphImage :imageSrc="props.mglyph2Src" :showShadow="false" />
      </div>
    </div>

    <div
      class="button-container"
      :class="buttonOrder === evaluationStore.ButtonOrderEnum.default ? '' : ' reversed'"
    >
      <button
        class="answer-button"
        :class="selectedAnswer === 'greater' ? 'selected' : ''"
        @click="onClickAnswer('greater')"
      >
        >
      </button>

      <button
        class="answer-button"
        :class="selectedAnswer === 'equal' ? 'selected' : ''"
        @click="onClickAnswer('equal')"
      >
        =
      </button>

      <button
        class="answer-button"
        :class="selectedAnswer === 'less' ? 'selected' : ''"
        @click="onClickAnswer('less')"
      >
        <
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import MGlyphImage from '@/components/MGlyphImage.vue'
import { evaluationStore } from '@/main'
import { ref, watch, onBeforeUnmount } from 'vue'

interface Props {
  mglyph1Src: string
  mglyph2Src: string
  onAnswer: (answer: 'greater' | 'equal' | 'less') => void
}

const props = defineProps<Props>()

type AnswerType = 'greater' | 'equal' | 'less'

const isAnimating = ref(false)
const selectedAnswer = ref<AnswerType | null>(null)
const buttonOrder = ref(evaluationStore.getConfigurationOrDefault().buttonOrder)
const glyphWidthPx = ref(evaluationStore.getConfigurationOrDefault().glyphWidthPx)

function onClickAnswer(answer: AnswerType) {
  if (isAnimating.value) return
  props.onAnswer(answer)
  isAnimating.value = true
  selectedAnswer.value = answer
  setTimeout(() => {
    isAnimating.value = false
    selectedAnswer.value = null
  }, 500)
}

function handleKeyDown(event: KeyboardEvent) {
  if (isAnimating.value) return
  if (event.key === 'ArrowLeft') {
    onClickAnswer(
      buttonOrder.value === evaluationStore.ButtonOrderEnum.default ? 'greater' : 'less',
    )
  } else if (event.key === 'ArrowDown') {
    onClickAnswer('equal')
  } else if (event.key === 'ArrowRight') {
    onClickAnswer(
      buttonOrder.value === evaluationStore.ButtonOrderEnum.default ? 'less' : 'greater',
    )
  }
}

window.addEventListener<'keydown'>('keydown', handleKeyDown)

onBeforeUnmount(() => {
  window.removeEventListener<'keydown'>('keydown', handleKeyDown)
})

watch(
  () => evaluationStore.getConfigurationOrDefault(),
  (newConfig) => {
    buttonOrder.value = newConfig.buttonOrder
    glyphWidthPx.value = newConfig.glyphWidthPx
  },
  { deep: true },
)
</script>

<style lang="css" scoped>
.sort-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  border-radius: 0.75rem;
  border: 2px solid rgb(var(--md-sys-color-outline, 103, 99, 94));
  padding: 2.5rem 4.5rem;

  background-color: white;
  width: min-content;
}

.glyphs-container {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 5rem;
}

.button-container {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 2rem;

  &.reversed {
    flex-direction: row-reverse;
  }

  .answer-button {
    font-size: 2.25rem;
    font-weight: 500;
    border: 0.15rem solid #444;
    color: #444;
    padding: 0 1.25rem;
    border-radius: 0.75rem;
    cursor: pointer;
    background-color: transparent;
  }
}

.glyph-image-container {
  width: v-bind(glyphWidthPx + 'px');
  aspect-ratio: 1/1;
}

/* Animations */

.sort-container.animated {
  .answer-button.selected {
    animation: buttonKeyframe 0.5s ease;
  }

  .glyph-image-container {
    animation: newGlyphPairKeyframe 0.5s ease;
  }
}

@keyframes buttonKeyframe {
  0% {
    background-color: transparent;
    border-color: #444;
  }

  50% {
    background-color: rgb(157, 213, 230);
    border-color: rgb(0, 39, 51);
    color: rgb(0, 39, 51);
  }

  100% {
    background-color: transparent;
    border-color: #444;
  }
}

@keyframes newGlyphPairKeyframe {
  0% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }

  100% {
    transform: scale(1);
  }
}
</style>
