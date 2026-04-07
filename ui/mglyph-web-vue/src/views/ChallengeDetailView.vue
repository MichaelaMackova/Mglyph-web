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
          :items="glyphsData || []"
          :items-length="10"
          :headers="[
            { title: '#', key: 'rank' },
            { title: 'Author', key: 'author' },
            { title: 'Glyph', key: 'glyph', sortable: false },
            { title: 'Flags', key: 'flags', sortable: false },
          ]"
          :items-per-page="glyphsItemsPerPage"
          :loading="glyphsLoading"
          @update:options="
            ({ page, itemsPerPage, sortBy }) => {
              glyphsCurrentPage = 1
              fetchPaginatedGlyphsData(page, itemsPerPage, getOrderByParam(sortBy[0]))
            }
          "
          sort-asc-icon="fa-solid fa-sort-up"
          sort-desc-icon="fa-solid fa-sort-down"
          sort-icon="fa-solid fa-sort"
          :fixed-header="true"
          height="min-content"
          :no-data-text="'No data available.'"
        >
          <template v-slot:item.rank="{ item }">
            {{ item.rank !== null ? item.rank : '-' }}
          </template>

          <template v-slot:item.author="{ item }">
            {{ item.author.username }}
          </template>

          <template v-slot:item.glyph="{ item }">
            <div class="glyph-image">
              <MGlyphPreviewImage :file_id="item.file_id" />
            </div>
          </template>

          <template v-slot:item.flags="{ item }">
            {{ item.flags.join(', ') }}
          </template>

          <template v-slot:bottom>
            <v-pagination
              :model-value="glyphsCurrentPage"
              @update:model-value="
                (newPage) => {
                  glyphsCurrentPage = newPage
                  fetchPaginatedGlyphsData(newPage, glyphsItemsPerPage)
                }
              "
              :length="glyphsTotalPages"
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
import SolverIcon from '@/components/icons/SolverIcon.vue'
import EvaluatorIcon from '@/components/icons/EvaluatorIcon.vue'
import MGlyphPreviewImage from '@/components/MGlyphPreviewImage.vue'
import {
  ChallengeDetail,
  ChallengeGlyph,
  ChallengeUserSolverRelationshipType,
  ChallengeUserEvaluatorRelationshipType,
} from '@/services/types'
import { mglyphClient } from '@/clients/mglyph_client'
import { authStore } from '@/main'
import { useRouter, type LocationQuery } from 'vue-router'
import { ref } from 'vue'
const router = useRouter()

const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)
const glyphsLoading = ref<boolean>(true)
const glyphsCurrentPage = ref<number>(1)
const glyphsTotalPages = ref<number>(1)
const glyphsItemsPerPage = 10
const challengeData = ref<ChallengeDetail | null>(null)
const glyphsData = ref<ChallengeGlyph[] | null>(null)

type OrderByParam = 'rank_asc' | 'rank_desc' | 'creator_asc' | 'creator_desc'

function getOrderByParam(
  sortBy: { key: string; order: 'asc' | 'desc' } | null,
): OrderByParam | null {
  if (!sortBy) return null
  switch (sortBy.key) {
    case 'rank':
      return sortBy.order === 'asc' ? 'rank_asc' : 'rank_desc'
    case 'author':
      return sortBy.order === 'asc' ? 'creator_asc' : 'creator_desc'
    default:
      return null
  }
}

async function fetchChallengeData() {
  try {
    // Simulate an API call to fetch challenge data
    const response = await mglyphClient.get(`/challenges/${router.currentRoute.value.params.id}`, {
      authorizeEndpoint: authStore.user ? true : false,
    })
    challengeData.value = ChallengeDetail.fromAPIResponse(response.data)
  } catch (error) {
    console.error('Error fetching challenge data:', error)
    errorOccurred.value = true
  } finally {
    isLoading.value = false
  }
}

async function fetchPaginatedGlyphsData(
  page: number,
  itemsPerPage: number,
  orderBy: OrderByParam | null = null,
) {
  glyphsLoading.value = true
  try {
    const response = await mglyphClient.get(
      `/challenges/${router.currentRoute.value.params.id}/glyphs`,
      {
        authorizeEndpoint: false,
        params: {
          page: page,
          size: itemsPerPage,
          order_by: orderBy,
        },
      },
    )
    glyphsData.value = response.data.items.map((glyph: any) => {
      return ChallengeGlyph.fromAPIResponse(glyph)
    })
    glyphsTotalPages.value = response.data.total_pages
    glyphsCurrentPage.value = response.data.page
  } catch (error) {
    console.error('Error fetching glyphs data:', error)
    // TODO: Add popup error message
  } finally {
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

  .glyph-image {
    margin: 8px 0;
    height: 100px;
    width: 100px;
  }
}

/* == table styles == */

.v-table {
  &::v-deep(th) {
    background-color: color-mix(
      in srgb,
      var(--md-sys-color-outline, #67635e) 25%,
      var(--md-sys-color-surface, #fff8f4)
    );
    font-weight: bold;
  }
}

/* ================== */
</style>
