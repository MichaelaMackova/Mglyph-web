<template>
  <div class="main-padding">
    <div v-if="isLoading" class="top-margin">
      Loading challenge data... <i class="fa-solid fa-spinner fa-spin-pulse"></i>
    </div>
    <div v-else-if="errorOccurred || !challengeData" class="top-margin">
      <PopupNote
        message="An error occurred while fetching challenge data. Please try again later."
        type="error"
        :closable="false"
        width="max-content"
      />
    </div>
    <div v-else>
      <div class="title-and-state">
        <h1>{{ challengeData.challenge.title }}</h1>

        <div class="state-and-user-info">
          <ChallengeState :state="challengeData.challenge.state" />
          <div class="user-info">
            <SolverIcon
              v-show="
                challengeData.user_relationship?.user_solver_relationship &&
                challengeData.user_relationship?.user_solver_relationship !==
                  ChallengeUserSolverRelationshipType.none
              "
            />
            <EvaluatorIcon
              v-show="
                challengeData.user_relationship?.user_evaluator_relationship &&
                challengeData.user_relationship?.user_evaluator_relationship !==
                  ChallengeUserEvaluatorRelationshipType.none
              "
            />
          </div>
        </div>
      </div>

      <div class="info-piece">
        <span class="label">Created:</span>
        {{
          challengeData.challenge.start_time.toLocaleString([], {
            dateStyle: 'long',
            timeStyle: 'short',
          })
        }}
      </div>
      <div class="info-piece">
        <span class="label">Submissions deadline:</span>
        {{
          challengeData.challenge.submission_deadline.toLocaleString([], {
            dateStyle: 'long',
            timeStyle: 'short',
          })
        }}
      </div>
      <div class="info-piece">
        <span class="label">Evaluations estimated until:</span>
        {{
          challengeData.challenge.evaluation_deadline.toLocaleString([], {
            dateStyle: 'long',
            timeStyle: 'short',
          })
        }}
      </div>

      <!-- NOTE: possible expansion: choose round (implement multiple rounds) -->
      <div class="glyph-table">
        <v-data-table-server
          :filter-keys="['name']"
          :items="[
            {
              rank: 1,
              author: 'User 1',
              img: 'https://via.placeholder.com/50',
              flags: ['flag1', 'flag2'],
            },
            {
              rank: 2,
              author: 'User 2',
              img: 'https://via.placeholder.com/50',
              flags: ['flag3', 'flag4'],
            },
          ]"
          :items-length="10"
          :headers="[
            { title: '#', key: 'rank' },
            { title: 'Author', key: 'author' },
            { title: 'Glyph', key: 'img' },
            { title: 'Flags', key: 'flags' },
          ]"
          :items-per-page="10"
          :loading="glyphsLoading"
          @update:options="
            ({ page, itemsPerPage, sortBy }) => {
              console.log('Options updated - fetch glyphs:', { page, itemsPerPage, sortBy })
            }
          "
          sort-asc-icon="fa-solid fa-sort-up"
          sort-desc-icon="fa-solid fa-sort-down"
          sort-icon="fa-solid fa-sort"
        >
          <template v-slot:bottom>
            <v-pagination
              :model-value="glyphsCurrentPage"
              @update:model-value="() => {}"
              :length="1"
              :total-visible="5"
              next-icon="fa-solid fa-caret-right"
              prev-icon="fa-solid fa-caret-left"
            ></v-pagination>
          </template>
        </v-data-table-server>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import PopupNote from '@/components/PopupNote.vue'
import ChallengeState from '@/components/ChallengeState.vue'
import SolverIcon from '@/components/SolverIcon.vue'
import EvaluatorIcon from '@/components/EvaluatorIcon.vue'
import {
  ChallengeDetail,
  ChallengeGlyph,
  ChallengeUserSolverRelationshipType,
  ChallengeUserEvaluatorRelationshipType,
} from '@/services/types'
import { mglyphClient } from '@/clients/mglyph_client'
import { useRouter, type LocationQuery } from 'vue-router'
import { ref } from 'vue'
const router = useRouter()

const isLoading = ref(true)
const errorOccurred = ref(false)
const glyphsLoading = ref(true)
const glyphsCurrentPage = ref(1)
const challengeData = ref<ChallengeDetail | null>(null)
const glyphsData = ref<ChallengeGlyph[] | null>(null)

async function fetchChallengeData() {
  try {
    // Simulate an API call to fetch challenge data
    const response = await mglyphClient.get(`/challenges/${router.currentRoute.value.params.id}`, {
      authorizeEndpoint: true,
    })
    challengeData.value = ChallengeDetail.fromAPIResponse(response.data)
  } catch (error) {
    console.error('Error fetching challenge data:', error)
    errorOccurred.value = true
  } finally {
    isLoading.value = false
    glyphsLoading.value = false
  }
}

fetchChallengeData()
</script>

<style lang="css" scoped>
.top-margin {
  margin-top: 20px;
}

.title-and-state {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.state-and-user-info {
  display: flex;
  flex-direction: row-reverse;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;

  .user-info {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  i {
    font-size: 130%;
  }
}

.info-piece {
  margin: 6px 0;

  .label {
    font-weight: bold;
    margin-right: 4px;
  }
}

.glyph-table {
  margin-top: 24px;
}

/* == table styles == */

.v-table {
  &::v-deep th {
    background-color: color-mix(in srgb, var(--md-sys-color-outline, #67635e) 25%, transparent);
    font-weight: bold;
  }
}

/* ================== */
</style>
