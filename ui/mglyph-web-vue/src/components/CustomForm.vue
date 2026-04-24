<template>
  <v-form ref="formRef" @submit.prevent="submitForm" v-model="valid" :disabled="props.isLoading">
    <!-- `.prevent` prevents reloading the page on submit -->
    <div class="form-container">
      <slot></slot>
      <button class="submit-button" type="submit" :disabled="props.isLoading">
        <i v-if="props.isLoading" class="fas fa-spinner fa-spin"></i>
        <span v-else>
          {{ props.submitText }}
        </span>
      </button>
    </div>
  </v-form>
</template>

<script lang="ts" setup>
import { ref, useTemplateRef } from 'vue'
interface Props {
  submitText: string
  onSubmit: (isFormValid: boolean | null) => void
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
})

const valid = ref<boolean | null>(null)
const formEl = useTemplateRef('formRef')

function submitForm() {
  if (props.isLoading) return

  if (formEl.value) {
    formEl.value
      .validate()
      .then(
        (validationResult: {
          valid: boolean
          errors: { id: string | number; errorMessages: string[] }[]
        }) => {
          props.onSubmit(validationResult.valid)
        },
      )
  } else {
    props.onSubmit(valid.value)
  }
}
</script>

<style lang="css" scoped>
.form-container {
  display: flex;
  flex-direction: column;
  /* justify-content: center;
  align-items: center; */
  gap: 1rem;
  max-width: 750px;

  --v-theme-error: var(--md-sys-color-error, 230, 141, 141);
  --v-theme-on-error: var(--md-sys-color-on-error, 255, 255, 255);
  --v-theme-error-overlay-multiplier: 0.12;
}

.submit-button {
  align-self: center;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  font-weight: bold;
  background-color: rgb(var(--md-sys-color-tertiary, 0, 129, 167));
  color: rgb(var(--md-sys-color-on-tertiary, 255, 255, 255));
  border: none;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
  min-width: min(300px, 100%);
  max-width: max-content;
}

.v-form::v-deep(.v-field:has(input[required])) {
  .v-label {
    padding-inline-end: 8px;

    &::after {
      position: absolute;
      content: '*';
      color: red;
      top: 0;
      inset-inline-end: 0; /* to support also RTL direction */
    }
  }
}
</style>
