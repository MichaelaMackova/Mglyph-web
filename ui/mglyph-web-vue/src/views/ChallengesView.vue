<template>
  <div class="main-padding">
    <h1>Challenges</h1>
    <p>Welcome to the challenges page!</p>
  </div>

  <div
    class="challenge-info-container main-padding"
    v-for="challenge in responseData"
    :key="challenge.id"
  >
    <ChallengeInfo
      :title="challenge.title"
      :start_time="challenge.start_time"
      :end_time="challenge.end_time"
      :state="challenge.state"
    />
  </div>

  <!-- TODO: paggination -->
</template>

<script setup lang="ts">
import ChallengeInfo from '@/components/ChallengeInfo.vue'
import { mglyphClient } from '@/clients/mglyph_client'
import { ref } from 'vue'
import { ChallengeStateEnum, ChallengeSimple } from '@/services/types'

const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)
const responseData = ref<ChallengeSimple[] | null>(null)

async function fetchChallenges() {
  try {
    const response = await mglyphClient.get('/challenges', {
      authorizeEndpoint: false,
      params: {
        offset: 0,
        limit: 100,
      },
    })
    console.log('Fetched challenges:', response.data)
    if (!Array.isArray(response.data)) {
      throw new Error('Invalid response format: expected an array')
    }
    responseData.value = response.data.map(
      (challenge: any) =>
        new ChallengeSimple(
          challenge.id,
          challenge.name,
          new Date(2021, 0, 1), // TODO: Replace with actual start time from response
          new Date(challenge.glyph_submit_deadline), // TODO: Replace with actual end time from response
          //challenge.submissions_ended,
          true,
          challenge.challenge_finished,
        ),
    )
    console.log('Parsed challenges:', responseData.value)
    errorOccurred.value = false
  } catch (err) {
    console.error(err)
    errorOccurred.value = true
  } finally {
    isLoading.value = false
  }
}
fetchChallenges()
</script>

<style scoped lang="css">
.challenge-info-container {
  padding-top: 20px;
  padding-bottom: 20px;

  background-color: var(--md-sys-color-surface, #fff8f4);
  color: var(--md-sys-color-on-surface, #201b13);

  &:nth-child(odd) {
    background-color: var(--md-sys-color-surface-variant, #fef1e5);
    color: var(--md-sys-color-on-surface-variant, #171511);
  }
}
</style>
