import { defineStore } from 'pinia'
import { ref } from 'vue'

const usePopupStore = defineStore('popup', () => {
  enum PopupTypeEnum {
    info = 'info',
    warning = 'warning',
    error = 'error',
  }

  class Popup {
    message: string
    type: PopupTypeEnum
    id: number

    constructor(message: string, type: PopupTypeEnum) {
      this.message = message
      this.type = type
      this.id = Date.now()
    }
  }

  const popups = ref<Popup[]>([])

  function addPopup(message: string, type: PopupTypeEnum) {
    popups.value.push(new Popup(message, type))
  }

  function removePopup(index: number) {
    if (index >= 0 && index < popups.value.length) {
      popups.value.splice(index, 1)
    }
  }

  return {
    PopupTypeEnum,
    Popup,
    popups,
    addPopup,
    removePopup,
  }
})

export { usePopupStore }
