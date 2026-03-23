<template>
  <div class="main-padding">
    <h1>Challenges</h1>
  </div>

  <div class="challenges-container">
    <div v-if="isLoading || errorOccurred" class="main-padding">
      <p v-if="isLoading">
        Loading challenges... <i class="fa-solid fa-spinner fa-spin-pulse"></i>
      </p>
      <p v-else-if="errorOccurred">An error occurred while fetching challenges.</p>
    </div>
    <div v-else-if="responseData && responseData.length === 0" class="main-padding">
      <p>No challenges available.</p>
    </div>
    <div
      v-else
      class="challenge-info-container main-padding"
      v-for="challenge_info in responseData"
      :key="challenge_info.challenge.id"
    >
      <ChallengeInfo
        :title="challenge_info.challenge.title"
        :start_time="challenge_info.challenge.start_time"
        :end_time="challenge_info.challenge.end_time"
        :state="challenge_info.challenge.state"
        :challengeGlyphs="challenge_info.glyphs"
        :user_solver_relationship="challenge_info.user_relationship?.user_solver_relationship"
        :user_evaluator_relationship="challenge_info.user_relationship?.user_evaluator_relationship"
      />
    </div>
  </div>

  <!-- TODO: pagination -->
</template>

<script setup lang="ts">
import ChallengeInfo from '@/components/ChallengeInfo.vue'
import { mglyphClient } from '@/clients/mglyph_client'
import { ref } from 'vue'
import { ChallengeStateEnum, ChallengeSimple, ChallengeGlyph, User } from '@/services/types'
import { authStore } from '@/main'

const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)
const responseData = ref<
  | {
      challenge: ChallengeSimple
      glyphs: ChallengeGlyph[]
      user_relationship: {
        user_solver_relationship?: 'none' | 'registered' | 'mglyph_submitted'
        user_evaluator_relationship?:
          | 'none'
          | 'registered'
          | 'evaluation_awaiting'
          | 'evaluation_finished'
      } | null
    }[]
  | null
>(null)

async function fetchChallenges() {
  try {
    const response = await mglyphClient.get('/challenges', {
      authorizeEndpoint: authStore.user ? true : false,
      params: {
        glyph_count: 3,
        offset: 0,
        limit: 100,
      },
    })
    if (!Array.isArray(response.data)) {
      throw new Error('Invalid response format: expected an array')
    }
    responseData.value = response.data.map((challenge: any) => {
      var ch = new ChallengeSimple(
        challenge.id,
        challenge.name,
        new Date(2021, 0, 1), // TODO: Replace with actual start time from response
        new Date(challenge.glyph_submit_deadline), // TODO: Replace with actual end time from response
        challenge.submissions_ended,
        challenge.challenge_finished,
      )
      var glyphs = challenge.mglyph_evaluations.map((glyph: any) => {
        return new ChallengeGlyph(
          glyph.malleable_glyph.id,
          glyph.rank,
          new User(glyph.malleable_glyph.creator.id, glyph.malleable_glyph.creator.username),
          new Array<string>(), // TODO: Replace with actual flags from response
        )
      })
      return {
        challenge: ch,
        glyphs: glyphs,
        user_relationship: {
          user_solver_relationship: challenge.user_relationship?.solver_relationship,
          user_evaluator_relationship: challenge.user_relationship?.evaluator_relationship,
        },
      }
    })
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
.challenges-container {
  padding-bottom: 20px;
}

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
