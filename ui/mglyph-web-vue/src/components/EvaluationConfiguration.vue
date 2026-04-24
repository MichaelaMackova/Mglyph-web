<template>
  <div class="button-order-selection">
    <div class="instructions">
      <h3>Sorting Buttons Order</h3>
      <p>Select the order in which you want the buttons to appear.</p>
    </div>

    <div
      class="button-container"
      v-for="i in 2"
      :key="i"
      :class="{
        reversed: i === 2,
        active:
          currentConfig.buttonOrder ===
          (i === 1
            ? evaluationStore.ButtonOrderEnum.default
            : evaluationStore.ButtonOrderEnum.reversed),
      }"
      @click="i === 1 ? setDefaultButtonOrder() : setReversedButtonOrder()"
    >
      <div class="answer-button">></div>
      <div class="answer-button">=</div>
      <div class="answer-button"><</div>
    </div>
  </div>
  <div class="width-calibration">
    <div class="instructions">
      <h3>Glyph Size Calibration</h3>
      <p>
        <b>Adjust this rectangle to match your credit card.</b>
        <br />
        If you don't have a credit card, use a ruler to measure the 1 inch square (2.54 cm).
      </p>
    </div>

    <div class="card-container">
      <div class="card">
        <div class="inch">
          <span>1 inch</span>
        </div>
        <span class="card-width">{{ cardWidthPx.toFixed(0) }}px</span>
      </div>
    </div>

    <div class="userInput">
      <v-slider
        v-model="dpi"
        @update:modelValue="onDpiChange"
        :max="360"
        :min="60"
        :step="1"
        :thumb-label="false"
        hide-details
      >
      </v-slider>
      <div class="dpi-value">DPI: {{ dpi }}</div>
    </div>
  </div>
  <button class="complete-button" @click="onSetupComplete">Setup Complete</button>
</template>

<script lang="ts" setup>
import { evaluationStore } from '@/main'
import { ref } from 'vue'

// CONSTANTS
const mmPerInch = 25.4
// ISO/IEC 7810 standard
const creditCardWidthMm = 85.6
const creditCardHeightMm = 53.98

const emit = defineEmits<{
  (e: 'setupComplete'): void
}>()
const currentConfig = ref(evaluationStore.getConfigurationOrDefault())
const dpi = ref(currentConfig.value.glyphWidthPx)
const cardWidthPx = ref(0)
const cardHeightPx = ref(0)

function onSetupComplete() {
  emit('setupComplete')
  evaluationStore.updateConfiguration(
    currentConfig.value.buttonOrder,
    currentConfig.value.glyphWidthPx,
  )
}

function onDpiChange() {
  calculateCardDimensionsPx()
  setGlyphWidth(dpi.value)
}

function calculateCardDimensionsPx() {
  cardWidthPx.value = (creditCardWidthMm / mmPerInch) * dpi.value
  cardHeightPx.value = (creditCardHeightMm / mmPerInch) * dpi.value
}

function setDefaultButtonOrder() {
  evaluationStore.updateConfiguration(evaluationStore.ButtonOrderEnum.default)
  currentConfig.value = evaluationStore.getConfigurationOrDefault()
}

function setReversedButtonOrder() {
  evaluationStore.updateConfiguration(evaluationStore.ButtonOrderEnum.reversed)
  currentConfig.value = evaluationStore.getConfigurationOrDefault()
}

function setGlyphWidth(width: number) {
  evaluationStore.updateConfiguration(null, width)
  currentConfig.value = evaluationStore.getConfigurationOrDefault()
}

calculateCardDimensionsPx()
</script>

<style lang="css" scoped>
.button-order-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.instructions {
  width: 100%;
}

.button-container {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  cursor: pointer;
  border: 0.1rem solid rgb(var(--md-sys-color-outline, 103, 99, 94));
  padding: 0.5rem;
  border-radius: 0.75rem;
  background-color: white;

  &.reversed {
    flex-direction: row-reverse;
  }

  &.active {
    border-color: rgb(var(--md-sys-color-secondary, 0, 175, 185));
    border-width: 0.2rem;
  }

  .answer-button {
    font-size: 2.25rem;
    font-weight: 500;
    border: 0.15rem solid #444;
    color: #444;
    padding: 0 1.25rem;
    border-radius: 0.75rem;
    background-color: transparent;
  }
}

.width-calibration {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card-container {
  width: 100%;
  height: 380px;
  overflow: hidden;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0.1rem dashed rgba(var(--md-sys-color-outline, 103, 99, 94), 0.3);

  .card {
    width: v-bind(cardWidthPx + 'px');
    height: v-bind(cardHeightPx + 'px');

    padding-bottom: 0.25rem;
    background-color: #888;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    position: relative;

    .card-width {
      color: var(--page-bg);
      position: absolute;
      bottom: 2%;
    }

    .inch {
      --inch-px: v-bind(dpi + 'px');
      width: var(--inch-px);
      height: var(--inch-px);

      border: 0.1rem solid currentColor;
      text-align: center;
      align-content: center;
      color: var(--page-bg);
    }
  }
}

.userInput {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  width: 30rem;
  max-width: 100%;
}

.v-slider {
  width: 100%;
  --v-theme-surface-variant: var(--md-sys-color-on-surface, 32, 27, 19);
  --v-theme-on-surface-variant: var(--md-sys-color-surface, 255, 248, 244);
}

.complete-button {
  margin-top: 2rem;
  padding: 0.75rem 1.5rem;
  font-size: 1.1rem;
  color: rgb(var(--md-sys-color-on-tertiary, 255, 255, 255));
  background-color: rgb(var(--md-sys-color-tertiary, 0, 129, 167));
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
}
</style>
