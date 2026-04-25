<template>
  <div class="main-padding">
    <div v-if="!authStore.user" class="main-top-margin">
      <PopupNote
        message="You must be logged in to access this page."
        type="error"
        width="max-content"
      />
    </div>
    <!-- TODO: není přihlášený jako solver -->
    <!-- TODO: již uploadnul mglyph -->
    <div v-else>
      <h1>Create Malleable Glyph</h1>
      <CustomForm
        submitText="Create Malleable Glyph"
        :onSubmit="submitForm"
        :isLoading="isFormLoading"
      >
        <v-text-field
          v-model="longNameInput.modelValue"
          :rules="longNameInput.rules"
          :error-messages="longNameInput.errorMessages"
          :label="longNameInput.label"
          :type="longNameInput.type"
          :required="longNameInput.required"
          hide-details="auto"
        ></v-text-field>
        <v-text-field
          v-model="shortNameInput.modelValue"
          :rules="shortNameInput.rules"
          :error-messages="shortNameInput.errorMessages"
          :label="shortNameInput.label"
          :type="shortNameInput.type"
          :required="shortNameInput.required"
          hide-details="auto"
          persistent-hint
          hint="Short name must be at most 20 characters long and cannot contain spaces."
        ></v-text-field>
        <v-textarea
          class="code"
          v-model="codeTextArea.modelValue"
          :rules="codeTextArea.rules"
          :error-messages="codeTextArea.errorMessages"
          :label="codeTextArea.label"
          :required="codeTextArea.required"
          hide-details="auto"
          rows="8"
          clearable
          clear-icon="fa-solid fa-circle-xmark"
        ></v-textarea>
        <v-switch
          v-model="isCodePublicSwitch.modelValue"
          :rules="isCodePublicSwitch.rules"
          :error-messages="isCodePublicSwitch.errorMessages"
          :label="isCodePublicSwitch.label"
          :required="isCodePublicSwitch.required"
          hide-details="auto"
          color="secondary"
          indeterminate
        ></v-switch>
        <v-file-input
          v-model="fileInput.modelValue"
          :rules="fileInput.rules"
          :error-messages="fileInput.errorMessages"
          :label="fileInput.label"
          :required="fileInput.required"
          :accept="fileInput.acceptTypes"
          show-size
          prepend-icon="fa-solid fa-upload"
          :clearable="false"
          clear-icon="fa-solid fa-circle-xmark"
          hide-details="auto"
        ></v-file-input>
      </CustomForm>
    </div>
  </div>
</template>

<script lang="ts" setup>
import PopupNote from '@/components/PopupNote.vue'
import CustomForm from '@/components/CustomForm.vue'
import { authStore, popupStore } from '@/main'
import { mglyphClient } from '@/clients/mglyph_client'
import { type AxiosResponse } from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

type FieldProps<T> = {
  modelValue: T
  label: string
  required: boolean
  rules: Array<(value: T) => boolean | string>
  errorMessages: string[]
}

type InputProps = FieldProps<string> & {
  type: string
}

type FileInputProps = FieldProps<File | null> & {
  acceptTypes?: string[]
}

const isFormLoading = ref(false)
const longNameInput = ref<InputProps>({
  modelValue: '',
  label: 'Long name',
  type: 'input',
  required: true,
  rules: [
    (value: string) => {
      if (value) return true
      return 'Long name is required.'
    },
  ],
  errorMessages: [],
})
const shortNameInput = ref<InputProps>({
  modelValue: '',
  label: 'Short name',
  type: 'input',
  required: true,
  rules: [
    (value: string) => {
      if (value) return true
      return 'Short name is required.'
    },
    (value: string) => {
      if (value.length <= 20) return true
      return 'Short name must be at most 20 characters long.'
    },
    (value: string) => {
      if (!/\s/.test(value)) return true
      return 'Short name cannot contain spaces.'
    },
  ],
  errorMessages: [],
})
const codeTextArea = ref<InputProps>({
  modelValue: '',
  label: 'Code',
  type: 'textarea',
  required: false,
  rules: [],
  errorMessages: [],
})
const isCodePublicSwitch = ref<FieldProps<boolean | null>>({
  modelValue: null,
  label: 'Code is publicly visible',
  required: true,
  rules: [
    (value: boolean | null) => {
      if (value !== null) return true
      return 'Please specify whether the code is publicly visible.'
    },
  ],
  errorMessages: [],
})
const fileInput = ref<FileInputProps>({
  modelValue: null,
  label: 'Upload mglyph file',
  required: true,
  acceptTypes: ['application/zip', 'application/x-zip-compressed', 'application/x-zip', '.mglyph'],
  rules: [
    (value: File | null) => {
      if (value) return true
      return 'Mglyph file is required.'
    },
    (value: File | null) => {
      if (!value) return true
      if (fileInput.value.acceptTypes) {
        const allowedTypes = fileInput.value.acceptTypes
        if (allowedTypes.includes(value.type) || value.name.endsWith('.mglyph')) {
          return true
        }
        return 'Invalid file type. Please upload a .zip or .mglyph file.'
      }
      return true
    },
  ],
  errorMessages: [],
})

async function createMGlyph(): Promise<AxiosResponse> {
  return mglyphClient.post(
    '/mglyph',
    {
      long_name: longNameInput.value.modelValue,
      short_name: shortNameInput.value.modelValue,
      code: codeTextArea.value.modelValue,
      is_code_public: isCodePublicSwitch.value.modelValue,
      challenge_id: router.currentRoute.value.params.id,
      zip_file: fileInput.value.modelValue,
    },
    {
      authorizeEndpoint: true,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    },
  )
}

async function submitForm(isFormValid: boolean | null): Promise<void> {
  isFormLoading.value = true
  longNameInput.value.errorMessages = []
  shortNameInput.value.errorMessages = []
  codeTextArea.value.errorMessages = []
  isCodePublicSwitch.value.errorMessages = []
  fileInput.value.errorMessages = []

  if (!isFormValid) {
    isFormLoading.value = false
    return
  }

  try {
    console.log('Submitting form')
    const response = await createMGlyph()
    popupStore.addPopup(
      `Malleable Glyph "${response.data.long_name}" created successfully!`,
      popupStore.PopupTypeEnum.info,
    )
    // Redirect to the newly created mglyph's detail page
    router.push({ name: 'MGlyphDetail', params: { id: response.data.id } })
  } catch (error: any) {
    if (error.response && error.response.data && error.response.data.err_code) {
      if (error.response.data.err_code === 206) {
        console.error('Error creating challenge:', error)
        popupStore.addPopup(
          'You have already submitted a malleable glyph for this challenge. Please delete your existing submission before creating a new one or edit your current one.',
          popupStore.PopupTypeEnum.error,
        )
      }
      // TODO: handle other specific error codes (e.g., invalid file format, missing fields, name is not unique, etc.)
      // if (error.response.data.err_code === 205) {
      //   challengeNameInput.value.errorMessages = ['A challenge with this name already exists.']
      //   return
      // }
    }
    console.error('Error creating challenge:', error)
    popupStore.addPopup(
      'Failed to create malleable glyph. Please try again.',
      popupStore.PopupTypeEnum.error,
    )
  } finally {
    isFormLoading.value = false
  }
}
</script>

<style lang="css" scoped>
.v-text-field.code::v-deep(textarea) {
  font-family: 'Courier New', Courier, monospace;
}

.v-switch {
  --v-theme-surface-variant: var(--md-sys-color-outline, 103, 99, 94); /* unselected - track */
  --v-theme-surface-bright: var(--md-sys-color-on-surface, 32, 27, 19); /* unselected - thumb */
  --v-theme-secondary: var(--md-sys-color-tertiary, 0, 129, 167); /* selected */
}
</style>
