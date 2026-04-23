<template>
  <div v-if="!authStore.user" class="main-top-margin main-padding">
    <PopupNote
      message="You need to be logged in to access this page."
      type="error"
      :closable="false"
      width="max-content"
    />
  </div>
  <div v-else>
    <div v-if="isLoading" class="main-top-margin main-padding">
      <p>Loading evaluation mglyphs... <i class="fa-solid fa-spinner fa-spin-pulse"></i></p>
    </div>
    <div v-else-if="errorOccurred" class="main-top-margin main-padding">
      <PopupNote
        message="An error occurred while loading the malleable glyphs for evaluation. Please try again later."
        type="error"
        :closable="false"
        width="max-content"
      />
    </div>
    <div v-else>
      <div v-if="evaluationMglyphs.length === 0">
        <PopupNote
          message="No evaluation mglyphs available."
          type="warning"
          :closable="false"
          width="max-content"
        />
      </div>
      <div v-else>
        <EvaluationViewTemplate :mglyphs="evaluationMglyphs" v-model="answersObj.answers" />
        <!-- TODO: End Evaluation Button -->
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import EvaluationViewTemplate from '@/components/EvaluationViewTemplate.vue'
import PopupNote from '@/components/PopupNote.vue'
import { ChallengeGlyph, EvaluateAnswer, User } from '@/services/types'
import { fetchZipFileAsArrayBuffer, unzip, type ZipFileContent } from '@/services/zip-file-utils'
import { authStore, popupStore } from '@/main'
import { mglyphClient } from '@/clients/mglyph_client'
import { useRouter } from 'vue-router'
import { ref, watch } from 'vue'
const router = useRouter()

type MGlyphData = {
  info: ChallengeGlyph
  file: ZipFileContent
}

type Answers = { answers: EvaluateAnswer[] }

const evaluationMglyphs = ref<MGlyphData[]>([])
const answersObj = ref<Answers>({ answers: [] }) // NOTE: wrap answers in an object to be able to watch for changes in the array and easily clear the array after sending the answers to the server
const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)

async function fetchEvaluationMglyphs() {
  isLoading.value = true
  errorOccurred.value = false
  evaluationMglyphs.value = []
  try {
    const mglyphsResponse = await mglyphClient.get(
      `/challenges/${router.currentRoute.value.params.id}/evaluate`,
      { authorizeEndpoint: true },
    )
    for (const mglyphData of mglyphsResponse.data) {
      const mglyphInfo = ChallengeGlyph.fromAPIResponse(mglyphData)
      const fileResponse = await fetchZipFileAsArrayBuffer(mglyphInfo.file_id)
      evaluationMglyphs.value.push({
        info: mglyphInfo,
        file: await unzip(fileResponse.data),
      })
    }
  } catch (error) {
    console.error('Error fetching evaluation mglyphs:', error)
    errorOccurred.value = true
  } finally {
    isLoading.value = false
  }
}

async function sendAnswersToServer() {
  try {
    await mglyphClient.post(
      `/challenges/${router.currentRoute.value.params.id}/evaluate`,
      answersObj.value.answers,
      { authorizeEndpoint: true },
    )
  } catch (error) {
    console.error('Error sending answers to server:', error)
    popupStore.addPopup(
      'An error occurred while sending your answers. Your last 10 answers have not been saved.',
      popupStore.PopupTypeEnum.error,
    )
    // Optionally, you can keep the answers in the array to retry sending later
  }
}

watch(answersObj.value, () => {
  if (answersObj.value.answers.length === 10) {
    // Send every 10 answers to the server
    sendAnswersToServer()
    answersObj.value.answers = [] // Clear answers after sending
  }
})

if (authStore.user) {
  fetchEvaluationMglyphs()
}
</script>

<style lang="css" scoped></style>
