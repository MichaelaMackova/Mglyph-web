<template>
  <div class="main-padding">
    <div v-if="authStore.user?.role !== 'admin'" class="main-top-margin">
      <PopupNote
        message="You do not have permission to access this page."
        type="error"
        width="max-content"
      />
    </div>
    <div v-else>
      <h1>Create Challenge</h1>
      <CustomForm submitText="Create Challenge" :onSubmit="submitForm">
        <v-text-field
          v-model="challengeNameInput.modelValue"
          :rules="challengeNameInput.rules"
          :error-messages="challengeNameInput.errorMessages"
          :label="challengeNameInput.label"
          :type="challengeNameInput.type"
          :required="challengeNameInput.required"
          hide-details="auto"
        ></v-text-field>

        <v-text-field
          v-model="mglyphSubmissionDeadlineInput.modelValue"
          :rules="mglyphSubmissionDeadlineInput.rules"
          :error-messages="mglyphSubmissionDeadlineInput.errorMessages"
          :label="mglyphSubmissionDeadlineInput.label"
          :type="mglyphSubmissionDeadlineInput.type"
          :required="mglyphSubmissionDeadlineInput.required"
          hide-details="auto"
          :min="dateToLocalISOLikeString(nowDate, false)"
        ></v-text-field>

        <v-text-field
          v-model="endTimeInput.modelValue"
          :rules="endTimeInput.rules"
          :error-messages="endTimeInput.errorMessages"
          :label="endTimeInput.label"
          :type="endTimeInput.type"
          :required="endTimeInput.required"
          hide-details="auto"
          :min="dateToLocalISOLikeString(nowDate, false)"
        ></v-text-field>
      </CustomForm>
    </div>
  </div>
</template>

<script lang="ts" setup>
import PopupNote from '@/components/PopupNote.vue'
import CustomForm from '@/components/CustomForm.vue'
import { dateToLocalISOLikeString, validateDateIsInFuture } from '@/services/date-format-utils'
import { authStore } from '@/main'
import { mglyphClient } from '@/clients/mglyph_client'
import { type AxiosResponse } from 'axios'
import { ref, watch } from 'vue'

type InputProps = {
  modelValue: string
  label: string
  type: string
  required: boolean
  rules: Array<(value: string) => boolean | string>
  errorMessages: string[]
}

const nowDate = new Date()
const challengeNameInput = ref<InputProps>({
  modelValue: '',
  label: 'Challenge name',
  type: 'input',
  required: true,
  rules: [
    (value: string) => {
      if (value) return true
      return 'Challenge name is required.'
    },
  ],
  errorMessages: [],
})
const mglyphSubmissionDeadlineInput = ref<InputProps>({
  modelValue: '',
  label: 'Malleable glyph submission deadline',
  type: 'datetime-local',
  required: true,
  rules: [
    (value: string) => {
      if (value) return true
      return 'Malleable glyph submission deadline is required.'
    },
    (value: string) =>
      validateDateIsInFuture(value) || 'Malleable glyph submission deadline must be in the future.',
  ],
  errorMessages: [],
})
const endTimeInput = ref<InputProps>({
  modelValue: '',
  label: 'End of challenge evaluations',
  type: 'datetime-local',
  required: true,
  rules: [
    (value: string) => {
      if (value) return true
      return 'End of challenge evaluations is required.'
    },
    (value: string) => validateDateIsInFuture(value) || 'End time must be in the future.',
    (value: string) =>
      !mglyphSubmissionDeadlineInput.value.modelValue ||
      new Date(value) > new Date(mglyphSubmissionDeadlineInput.value.modelValue) ||
      'End time must be after the malleable glyph submission deadline.',
  ],
  errorMessages: [],
})

async function createChallenge(): Promise<AxiosResponse> {
  return mglyphClient.post(
    '/challenges',
    {
      name: challengeNameInput.value.modelValue,
      glyph_submit_deadline: new Date(mglyphSubmissionDeadlineInput.value.modelValue).toISOString(),
      first_evaluation_round: {
        estimated_end_time: new Date(endTimeInput.value.modelValue).toISOString(),
      },
    },
    {
      authorizeEndpoint: true,
      headers: {
        'Content-Type': 'application/json',
      },
    },
  )
}

async function submitForm(isFormValid: boolean | null): Promise<void> {
  if (!isFormValid) return

  try {
    const response = await createChallenge()
    console.log('Challenge created successfully:', response.data)
    // Optionally, redirect to the challenge page or show a success message
  } catch (error) {
    console.error('Error creating challenge:', error)
    // Optionally, show an error message to the user
  }
}
</script>

<style lang="css" scoped></style>
