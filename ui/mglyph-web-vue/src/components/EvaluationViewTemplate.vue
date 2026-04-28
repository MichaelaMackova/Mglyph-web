<template>
  <div class="main-padding">
    <div v-if="props.mglyphs.length <= 0" class="main-top-margin">
      <PopupNote message="No evaluation mglyphs available." type="error" :closable="false" />
    </div>
    <div v-else-if="showConfig" class="main-top-margin configuration-container">
      <PopupNote
        v-show="showConfigPopup"
        message="You do not have configured evaluation setting on this device. Please configure the evaluation settings before starting the evaluation."
        type="warning"
        width="max-content"
        :closable="false"
      />
      <EvaluationConfiguration @setupComplete="onConfigComplete" />
    </div>
    <div v-else-if="currentGlyphIndex === null" class="main-top-margin">
      Loading... <i class="fas fa-spinner fa-pulse"></i>
    </div>
    <div v-else class="glyph-sort-container main-bottom-margin">
      <div class="glyph-sort-content">
        <button class="config-button" @click="showConfig = true">
          <i class="fa-solid fa-gear"></i>
        </button>
        <GlyphSortCard
          :onAnswer="onAnswer"
          :mglyph1Src="
            props.mglyphs[currentGlyphIndex]?.file.images[currentGlyphValIndex1 || 0]?.blobUrl || ''
          "
          :mglyph2Src="
            props.mglyphs[currentGlyphIndex]?.file.images[currentGlyphValIndex2 || 0]?.blobUrl || ''
          "
        />
        <div class="eval-button-container">
          <button class="eval-button" @click="onEndEvaluation">
            <div class="label-with-icon">
              <span class="label">End Evaluation</span>
              <span class="icon"><i class="fa-solid fa-arrow-right"></i></span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import PopupNote from '@/components/PopupNote.vue'
import GlyphSortCard from './GlyphSortCard.vue'
import EvaluationConfiguration from './EvaluationConfiguration.vue'
import { type ZipFileContent } from '@/services/zip-file-utils'
import { evaluationStore } from '@/main'
import { ChallengeGlyph, EvaluateAnswer } from '@/services/types'
import { getRandomInt } from '@/services/random-int'
import { Temporal } from 'temporal-polyfill'
import { ref, watch } from 'vue'

type MGlyphData = {
  info: ChallengeGlyph
  file: ZipFileContent
}

interface Props {
  mglyphs: MGlyphData[]
}
const props = defineProps<Props>()
const answers = defineModel<EvaluateAnswer[]>({
  required: true,
})
const emit = defineEmits<{
  (e: 'endEvaluation'): void
}>()

const showConfig = ref<boolean>(!evaluationStore.isConfigurationSet())
const showConfigPopup = ref<boolean>(!evaluationStore.isConfigurationSet())

const currentGlyphIndex = ref<number | null>(null)
const currentGlyphValIndex1 = ref<number | null>(null)
const currentGlyphValIndex2 = ref<number | null>(null)
const startTime = ref<Date | null>(null)
const endTime = ref<Date | null>(null)

const getGlyphAlgoHelpers = ref<
  ({
    isFirstInSession: boolean
    isLastCorrect?: boolean
    lastValsEqual?: boolean
    usedComputedDistancesBuffer: number[] // NOTE: store used distances to avoid computing the same distances over and over again (only t changes, so the distance is the same for the same t)
    lastDistanceIndex: number // NOTE: same as t
  } | null)[]
>(Array(props.mglyphs.length).fill(null)) // NOTE: index corresponds to the mglyph index
const getGlyphAlgoConfig = {
  tProgressStep: 1,
  tRegressStep: 3,
  gamma: 0.7,
  d0: 20.0,
}

function onAnswer(answer: 'greater' | 'equal' | 'less') {
  endTime.value = new Date()
  const currentHelper = getGlyphAlgoHelpers.value[currentGlyphIndex.value!]!
  saveAnswer(answer, currentHelper.usedComputedDistancesBuffer[currentHelper.lastDistanceIndex]!)
  const nextGlyphs = getNextGlyphs()
  saveGlyphHelper(
    currentGlyphIndex.value!,
    answers.value[answers.value.length - 1]!,
    nextGlyphs.helperDistanceIndex,
  )
  startNewGlyphEvaluation(nextGlyphs)
}

function saveAnswer(answer: 'greater' | 'equal' | 'less', calculatedDistance: number) {
  let currentGlyph = props.mglyphs[currentGlyphIndex.value || 0]!
  let newAnswer = new EvaluateAnswer(
    currentGlyph.info.id,
    currentGlyph.file.images[currentGlyphValIndex1.value || 0]?.glyphValue || -1,
    currentGlyph.file.images[currentGlyphValIndex2.value || 0]?.glyphValue || -1,
    calculatedDistance,
    answer,
    Temporal.Duration.from({
      milliseconds: endTime.value!.getTime() - startTime.value!.getTime(),
    }),
  )
  answers.value.push(newAnswer)
}

function getNextGlyphs() {
  const newGlyphIndex = getRandomInt(0, props.mglyphs.length - 1)
  const newComputedValues = getNewGlyphPairValues(
    newGlyphIndex,
    answers.value[answers.value.length - 1] || null,
  )
  return {
    newGlyphVal1Index: getClosestIndex(
      props.mglyphs[newGlyphIndex]!.file.images,
      newComputedValues.glyph1Val,
    ),
    newGlyphVal2Index: getClosestIndex(
      props.mglyphs[newGlyphIndex]!.file.images,
      newComputedValues.glyph2Val,
    ),
    newGlyphIndex: newGlyphIndex,
    helperDistanceIndex: newComputedValues.helperDistanceIndex,
  }
}

function startNewGlyphEvaluation(newGlyphValues: {
  newGlyphVal1Index: number
  newGlyphVal2Index: number
  newGlyphIndex: number
}) {
  currentGlyphValIndex1.value = newGlyphValues.newGlyphVal1Index
  currentGlyphValIndex2.value = newGlyphValues.newGlyphVal2Index
  currentGlyphIndex.value = newGlyphValues.newGlyphIndex
  endTime.value = null
  startTime.value = new Date()
}

function saveGlyphHelper(mglyphIndex: number, answer: EvaluateAnswer, distanceIndex: number) {
  let currentGlyphHelper = getGlyphAlgoHelpers.value[mglyphIndex]!
  if (answer.answered_symbol == 'equal') {
    currentGlyphHelper.lastValsEqual = true
    currentGlyphHelper.isLastCorrect = answer.first_glyph_value == answer.second_glyph_value
  } else {
    currentGlyphHelper.lastValsEqual = false
    if (answer.answered_symbol == 'greater') {
      currentGlyphHelper.isLastCorrect = answer.first_glyph_value > answer.second_glyph_value
    } else {
      currentGlyphHelper.isLastCorrect = answer.first_glyph_value < answer.second_glyph_value
    }
  }
  currentGlyphHelper.isFirstInSession = false
  currentGlyphHelper.lastDistanceIndex = distanceIndex
}

function getNewGlyphPairValues(
  mglyphIndex: number,
  answer: EvaluateAnswer | null,
): { glyph1Val: number; glyph2Val: number; helperDistanceIndex: number } {
  // NOTE:
  // right answer --> lastComputedDistance * (gamma ** tProgressStep)
  // wrong answer --> lastComputedDistance / (gamma ** tRegressStep)

  // check if mglyph was already used and if not, initialize the helper object
  if (getGlyphAlgoHelpers.value[mglyphIndex] == null) {
    getGlyphAlgoHelpers.value[mglyphIndex] = {
      isFirstInSession: true,
      isLastCorrect: undefined,
      lastValsEqual: undefined,
      usedComputedDistancesBuffer: [getGlyphAlgoConfig.d0],
      lastDistanceIndex: 0,
    }
  }
  let currentHelper = getGlyphAlgoHelpers.value[mglyphIndex]

  let computedDistance
  let val1
  let val2

  // GET DISTANCE

  // Get new index
  let newDistanceIndex
  if (!currentHelper.isFirstInSession) {
    if (currentHelper.lastValsEqual) {
      if (currentHelper.isLastCorrect) {
        newDistanceIndex = currentHelper.lastDistanceIndex
      } else {
        newDistanceIndex = currentHelper.lastDistanceIndex - getGlyphAlgoConfig.tRegressStep
      }
    } else {
      if (currentHelper.isLastCorrect) {
        newDistanceIndex = currentHelper.lastDistanceIndex + getGlyphAlgoConfig.tProgressStep
      } else {
        newDistanceIndex = currentHelper.lastDistanceIndex - getGlyphAlgoConfig.tRegressStep
      }
    }

    if (newDistanceIndex < 0) {
      newDistanceIndex = 0
    }
  } else {
    // first time, initialize distance index to 0
    newDistanceIndex = 0
  }

  // Get new distance
  // calculate distance if needed
  while (newDistanceIndex > currentHelper.usedComputedDistancesBuffer.length - 1) {
    let smallestDistance =
      currentHelper.usedComputedDistancesBuffer[
        currentHelper.usedComputedDistancesBuffer.length - 1
      ]!
    currentHelper.usedComputedDistancesBuffer.push(smallestDistance * getGlyphAlgoConfig.gamma)
  }

  computedDistance = currentHelper.usedComputedDistancesBuffer[newDistanceIndex]!

  // GET VALUES
  let offset = computedDistance / 2

  // Get the middle value. After adding or subtracting the offset, it cannot be lower than 0 or higher than the highest glyph.
  let midVal = getRandomInt(offset, 100 - offset - 1, 3)

  let futureAnswer = getRandomInt(0, 2) // 0 --> less, 1 --> greater, 2 --> equal
  if (futureAnswer == 0) {
    // less
    val1 = midVal - offset
    val2 = midVal + offset
  } else if (futureAnswer == 1) {
    // greater
    val1 = midVal + offset
    val2 = midVal - offset
  } else {
    // equal
    val1 = getRandomInt(0, 100 - 1, 3)
    val2 = val1
  }

  return {
    glyph1Val: val1,
    glyph2Val: val2,
    helperDistanceIndex: newDistanceIndex,
  }
}

function getClosestIndex(mglyphImages: { glyphValue: number }[], targetDistance: number) {
  let leftIndex = 0
  let rightIndex = mglyphImages.length - 1

  // binary search
  while (rightIndex - leftIndex > 1) {
    let midIndex = Math.floor((leftIndex + rightIndex) / 2)

    if (targetDistance > mglyphImages[midIndex]!.glyphValue) {
      leftIndex = midIndex
    } else {
      rightIndex = midIndex
    }
  }

  return Math.abs(mglyphImages[leftIndex]!.glyphValue - targetDistance) <=
    Math.abs(mglyphImages[rightIndex]!.glyphValue - targetDistance)
    ? leftIndex
    : rightIndex
}

function onConfigComplete() {
  showConfig.value = false
  showConfigPopup.value = !evaluationStore.isConfigurationSet()
}

function onEndEvaluation() {
  emit('endEvaluation')
}

watch(
  () => showConfig.value,
  (showConfigValue) => {
    if (showConfigValue) {
      showConfigPopup.value = !evaluationStore.isConfigurationSet()
    } else {
      startNewGlyphEvaluation(getNextGlyphs())
    }
  },
  { immediate: true },
)
</script>

<style lang="css" scoped>
.glyph-sort-container {
  margin-top: 7rem;
  display: flex;
  justify-content: center;
}

.glyph-sort-content {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  align-items: flex-start;
}

.config-button {
  font-size: 0.9rem;
  cursor: pointer;
  border-radius: 12px;
  padding: 6px;
  aspect-ratio: 1 / 1;
  background-color: rgb(var(--md-sys-color-secondary-container, 157, 226, 230));
  color: rgb(var(--md-sys-color-on-secondary-container, 0, 48, 51));
  border: 1px solid rgb(var(--md-sys-color-outline, 103, 99, 94));
  opacity: 0.7;

  &:hover {
    opacity: 1;
  }
}

.eval-button-container {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.eval-button {
  font-size: 1.1rem;
  cursor: pointer;
  border-radius: 50px;
  padding: 6px 12px;
  background-color: rgb(var(--md-sys-color-secondary, 0, 175, 185));
  color: rgb(var(--md-sys-color-on-secondary, 255, 255, 255));
  border: none;
  opacity: 0.8;

  &:hover {
    opacity: 1;
  }
}

.configuration-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 70vw;
  margin-left: auto;
  margin-right: auto;
}

.label-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;

  .icon {
    display: flex;
    align-items: center;
  }
}
</style>
