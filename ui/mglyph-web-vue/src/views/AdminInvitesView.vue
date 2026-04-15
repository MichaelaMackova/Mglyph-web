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
      <h1>Managing Evaluators And Invites</h1>
      <!-- Admin invites content goes here -->
      <v-data-table-server
        :items="challengeData?.items || []"
        :items-length="itemsPerPage"
        :headers="[
          { title: 'Challenge', key: 'title' },
          { title: 'Number of Active Evaluators', key: 'evaluators' },
          { title: 'State of Invites', key: 'invites' },
        ]"
        :items-per-page="itemsPerPage"
        :loading="isLoading"
        :loading-text="'Loading challenges...'"
        :no-data-text="
          errorOccurred
            ? 'An error occurred while fetching challenge data.'
            : 'No challenges found.'
        "
        :multi-sort="true"
        @update:options="
          ({ page, itemsPerPage, sortBy }) => {
            currentPage = 1
            console.log('Sorting by:', sortBy)
            fetchPaginatedData(page, itemsPerPage, getOrderByParam(sortBy))
          }
        "
        sort-asc-icon="fa-solid fa-sort-up"
        sort-desc-icon="fa-solid fa-sort-down"
        sort-icon="fa-solid fa-sort"
        :fixed-header="true"
        height="min-content"
      >
        <template v-slot:item.title="{ item }">
          <RouterLink :to="{ name: 'ChallengeDetail', params: { id: item.challenge.id } }">
            {{ item.challenge.title }}
          </RouterLink>
        </template>

        <template v-slot:item.evaluators="{ item }">
          {{ item.active_evaluator_count }}
        </template>

        <template v-slot:item.invites="{ item }">
          {{ item.has_pending_invites ? 'Pending' : 'None' }}
        </template>

        <template v-slot:bottom>
          <v-pagination
            :model-value="currentPage"
            @update:model-value="
              (newPage) => {
                currentPage = newPage
                fetchPaginatedData(newPage, itemsPerPage)
              }
            "
            :length="totalPages"
            :total-visible="5"
            next-icon="fa-solid fa-caret-right"
            prev-icon="fa-solid fa-caret-left"
          ></v-pagination>
        </template>
      </v-data-table-server>
    </div>
  </div>
</template>

<script lang="ts" setup>
import PopupNote from '@/components/PopupNote.vue'
import { ChallengeEvaluatorInvitesInfo, PaginatedData } from '@/services/types'
import { mglyphClient } from '@/clients/mglyph_client'
import { authStore, popupStore } from '@/main'
import { ref } from 'vue'

const challengeData = ref<PaginatedData<ChallengeEvaluatorInvitesInfo> | null>(null)
const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)
const itemsPerPage = 10
const currentPage = ref<number>(1)
const totalPages = ref<number>(1)

type OrderByParam =
  | 'evaluator_count_asc'
  | 'evaluator_count_desc'
  | 'pending_asc'
  | 'pending_desc'
  | 'ch_name_asc'
  | 'ch_name_desc'

function getOrderByParam(
  sortBy: { key: string; order: 'asc' | 'desc' }[] | null,
): OrderByParam[] | null {
  if (!sortBy || sortBy.length === 0) return null
  return sortBy
    .map((sort) => {
      switch (sort.key) {
        case 'evaluators':
          return sort.order === 'asc' ? 'evaluator_count_asc' : 'evaluator_count_desc'
        case 'invites':
          return sort.order === 'asc' ? 'pending_asc' : 'pending_desc'
        case 'title':
          return sort.order === 'asc' ? 'ch_name_asc' : 'ch_name_desc'
        default:
          return null
      }
    })
    .filter((param): param is OrderByParam => param !== null)
}

async function fetchPaginatedData(
  page: number,
  itemsPerPage: number,
  orderBy: OrderByParam[] | null = null,
) {
  isLoading.value = true
  errorOccurred.value = false

  try {
    const response = await mglyphClient.get(`/challenges/evaluator-invite-states`, {
      authorizeEndpoint: true,
      params: {
        page: page,
        size: itemsPerPage,
        order_by: orderBy,
        state: ['open', 'evaluating'],
      },
    })
    challengeData.value = PaginatedData.fromAPIResponse(
      response.data,
      ChallengeEvaluatorInvitesInfo.fromAPIResponse,
    )
    totalPages.value = challengeData.value.total_pages
    currentPage.value = challengeData.value.current_page
    console.log('Fetched challenge data:', challengeData.value)
  } catch (error) {
    console.error('Error fetching challenge data:', error)
    errorOccurred.value = true
  } finally {
    isLoading.value = false
  }
}
</script>

<style lang="css" scoped>
/* == table styles == */

.v-table {
  &::v-deep(th) {
    background-color: color-mix(
      in srgb,
      rgb(var(--md-sys-color-outline, 103, 99, 94)) 25%,
      rgb(var(--md-sys-color-surface, 255, 248, 244))
    );
    font-weight: bold;
  }
}

/* ================== */
</style>
