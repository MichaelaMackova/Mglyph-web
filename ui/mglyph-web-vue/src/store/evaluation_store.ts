import { defineStore } from 'pinia'
import { ref } from 'vue'

const useEvaluationStore = defineStore('evaluation', () => {
  enum ButtonOrderEnum {
    default = 'default',
    reversed = 'reversed',
  }

  class EvaluationConfiguration {
    buttonOrder: ButtonOrderEnum
    glyphWidthPx: number

    constructor(buttonOrder: ButtonOrderEnum, glyphWidthPx: number) {
      this.buttonOrder = buttonOrder
      this.glyphWidthPx = glyphWidthPx
    }
  }

  const configuration = ref<EvaluationConfiguration | null>(null)

  function initializeStoreFromLocalStorage() {
    const buttonOrder = localStorage.getItem('eval-config-buttonOrder')
    const glyphWidthPx = localStorage.getItem('eval-config-glyphWidthPx')

    if (buttonOrder || glyphWidthPx) {
      configuration.value = getDefaultConfiguration()

      if (buttonOrder) {
        if (buttonOrder === ButtonOrderEnum.default || buttonOrder === ButtonOrderEnum.reversed) {
          configuration.value.buttonOrder = buttonOrder as ButtonOrderEnum
        } else {
          console.warn(`Invalid button order in localStorage: ${buttonOrder}. Using default.`)
        }
      }

      if (glyphWidthPx) {
        const parsedGlyphWidthPx = parseInt(glyphWidthPx, 10)
        if (!isNaN(parsedGlyphWidthPx)) {
          configuration.value.glyphWidthPx = parsedGlyphWidthPx
        } else {
          console.warn(`Invalid glyph width in localStorage: ${glyphWidthPx}. Using default.`)
        }
      }
    }
  }

  function saveStoreToLocalStorage() {
    if (configuration.value) {
      localStorage.setItem('eval-config-buttonOrder', configuration.value.buttonOrder)
      localStorage.setItem('eval-config-glyphWidthPx', configuration.value.glyphWidthPx.toString())
    } else {
      localStorage.removeItem('eval-config-buttonOrder')
      localStorage.removeItem('eval-config-glyphWidthPx')
    }
  }

  function isConfigurationSet(): boolean {
    return configuration.value !== null
  }

  function getDefaultConfiguration(): EvaluationConfiguration {
    return new EvaluationConfiguration(ButtonOrderEnum.default, 96) // 96px is default html 1inch in pixels
  }

  function getConfigurationOrDefault(): EvaluationConfiguration {
    if (!configuration.value) {
      return getDefaultConfiguration()
    }
    return configuration.value
  }

  function resetConfiguration() {
    configuration.value = getDefaultConfiguration()
    saveStoreToLocalStorage()
  }

  function updateConfiguration(
    buttonOrder: ButtonOrderEnum | null = null,
    glyphWidthPx: number | null = null,
  ) {
    if (!configuration.value) {
      configuration.value = getDefaultConfiguration()
    }
    if (buttonOrder) {
      configuration.value.buttonOrder = buttonOrder
    }
    if (glyphWidthPx !== null) {
      configuration.value.glyphWidthPx = glyphWidthPx
    }
    saveStoreToLocalStorage()
  }

  return {
    ButtonOrderEnum,
    initializeStoreFromLocalStorage,
    updateConfiguration,
    isConfigurationSet,
    resetConfiguration,
    getConfigurationOrDefault,
  }
})

export { useEvaluationStore }
