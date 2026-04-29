<template>
  <div class="main-bottom-margin">
    <section class="hero main-padding">
      <div class="hero-copy">
        <h1>Welcome to The Malleable Glyph Challenge</h1>
        <p class="subtitle">
          Create glyphs, join challenges, and help advance research on malleable glyphs.
        </p>
        <p class="hero-text">
          Explore the newest challenges, sign in from the profile menu to participate, and keep
          track of your submissions and evaluations in one place.
        </p>

        <div class="hero-actions">
          <RouterLink class="primary-action" :to="{ name: 'Challenges' }"
            >Browse challenges</RouterLink
          >
          <RouterLink v-if="authStore.user" class="secondary-action" :to="{ name: 'MyChallenges' }">
            My challenges
          </RouterLink>
          <span v-else class="login-hint">Log in from the top-right menu to participate.</span>
        </div>
      </div>
    </section>

    <section class="main-padding info-grid">
      <article class="info-card">
        <p class="info-label">Latest challenges</p>
        <h2>See what is open right now.</h2>
        <p>The most recent challenges are listed below with their current state and key dates.</p>
      </article>

      <article class="info-card">
        <p class="info-label">Participation</p>
        <h2>Log in to submit and evaluate.</h2>
        <p>
          Use the profile menu in the header to sign in. Once logged in, you can follow your
          challenges and manage your glyphs.
        </p>
      </article>

      <article class="info-card">
        <p class="info-label">Navigation</p>
        <h2>Jump straight into the challenge list.</h2>
        <p>
          The challenge overview is the main entry point for browsing active rounds and opening a
          specific challenge.
        </p>
      </article>
    </section>

    <section class="latest-section">
      <div class="section-heading main-padding">
        <div>
          <h1>Latest challenges</h1>
        </div>
        <RouterLink class="section-link" :to="{ name: 'Challenges' }">View all</RouterLink>
      </div>

      <div v-if="isLoading" class="section-padding">
        Loading latest challenges... <i class="fas fa-spinner fa-pulse"></i>
      </div>
      <div v-else-if="errorOccurred" class="section-padding">
        <PopupNote
          message="We could not load the latest challenges right now."
          type="error"
          :closable="false"
          width="max-content"
        />
      </div>
      <div v-else-if="latestChallenges.length === 0" class="section-padding">
        No challenges are available yet.
      </div>
      <div v-else>
        <div
          class="challenge-info-container section-padding"
          v-for="challenge_info in latestChallenges"
          :key="challenge_info.challenge.id"
        >
          <ChallengeInfo
            :id="challenge_info.challenge.id"
            :title="challenge_info.challenge.title"
            :start_time="challenge_info.challenge.start_time"
            :submission_deadline="challenge_info.challenge.submission_deadline"
            :end_time="challenge_info.challenge.evaluation_deadline"
            :state="challenge_info.challenge.state"
            :challengeGlyphs="challenge_info.glyphs"
            :user_solver_relationship="
              challenge_info.user_relationship?.user_solver_relationship?.relationship_type
            "
            :user_evaluator_relationship="
              challenge_info.user_relationship?.user_evaluator_relationship
            "
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import ChallengeInfo from '@/components/ChallengeInfo.vue'
import PopupNote from '@/components/PopupNote.vue'
import { mglyphClient } from '@/clients/mglyph_client'
import { authStore } from '@/main'
import { ChallengeMiniDetail, PaginatedData } from '@/services/types'
import { ref } from 'vue'

const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)
const latestChallenges = ref<ChallengeMiniDetail[]>([])

async function fetchLatestChallenges() {
  isLoading.value = true
  errorOccurred.value = false
  try {
    const response = await mglyphClient.get('/challenges', {
      authorizeEndpoint: authStore.user ? true : false,
      params: {
        glyph_count: 3,
        page: 1,
        size: 3,
      },
    })

    if (!Array.isArray(response.data.items)) {
      throw new Error('Invalid response format: expected an array')
    }

    const paginatedData = PaginatedData.fromAPIResponse<ChallengeMiniDetail>(
      response.data,
      ChallengeMiniDetail.fromAPIResponse,
    )

    latestChallenges.value = paginatedData.items
  } catch (err) {
    console.error(err)
    errorOccurred.value = true
  } finally {
    isLoading.value = false
  }
}

fetchLatestChallenges()
</script>

<style scoped lang="css">
.challenge-info-container {
  padding-top: 20px;
  padding-bottom: 20px;

  background-color: rgb(var(--md-sys-color-surface, 255, 248, 244));
  color: rgb(var(--md-sys-color-on-surface, 32, 27, 19));

  &:nth-child(odd) {
    background-color: rgb(var(--md-sys-color-surface-variant, 254, 241, 229));
    color: rgb(var(--md-sys-color-on-surface-variant, 23, 21, 17));
  }
}

.latest-section {
  margin: 40px 0;

  .section-padding {
    padding-left: 50px;
    padding-right: 50px;
  }
}

.hero {
  padding-bottom: 24px;

  .hero-copy {
    padding: 28px;
  }

  h1 {
    font-size: 2.5em;
    line-height: 1;
    text-align: center;
  }

  p.subtitle {
    font-size: 120%;
    font-weight: bolder;
    font-style: italic;
  }

  .hero-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    margin-top: 32px;
  }

  .login-hint {
    font-size: 0.9em;
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 10px;
  margin-bottom: 16px;
}

.info-card {
  padding: 20px;
  background-color: rgb(var(--md-sys-color-surface-variant, 254, 241, 229));
  color: rgb(var(--md-sys-color-on-surface-variant, 23, 21, 17));
  border: 1px solid rgba(var(--md-sys-color-outline, 103, 99, 94), 0.06);
  border-radius: 20px;
  box-shadow: 2px 4px 8px rgba(var(--md-sys-color-outline, 103, 99, 94), 0.15);

  .info-label {
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.78rem;
  }
}

.primary-action,
.secondary-action,
.section-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 16px;
  border-radius: 999px;
  text-decoration: none;
  transition:
    transform 0.15s ease,
    box-shadow 0.15s ease,
    background-color 0.15s ease;
}

.primary-action {
  background-color: rgb(var(--md-sys-color-secondary, 0, 175, 185));
  color: rgb(var(--md-sys-color-on-primary, 255, 255, 255));
  box-shadow: -1px 4px 8px 0px rgba(var(--md-sys-color-outline), 0.3);
}

.secondary-action,
.section-link {
  border: 1px solid rgba(var(--md-sys-color-outline, 103, 99, 94), 0.1);
  background-color: rgb(var(--md-sys-color-secondary-container, 157, 226, 230));
  color: rgb(var(--md-sys-color-on-secondary-container, 0, 48, 51));
}

.primary-action:hover,
.secondary-action:hover,
.section-link:hover {
  transform: translateY(-1px);
}

.info-card h2,
.section-heading h1 {
  margin: 10px 0 10px;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 16px;
  margin-bottom: 12px;
}

@media (max-width: 900px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .section-heading {
    align-items: start;
    flex-direction: column;
  }
}

@media (max-width: 640px) {
  .hero-copy,
  .info-card,
  .state-box {
    border-radius: 16px;
  }

  .hero-copy {
    padding: 22px;
  }
}
</style>
