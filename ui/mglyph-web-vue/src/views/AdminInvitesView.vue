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
        :items="challengeData || []"
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
            fetchPaginatedData(page, itemsPerPage, getOrderByParam(sortBy[0]))
          }
        "
        sort-asc-icon="fa-solid fa-sort-up"
        sort-desc-icon="fa-solid fa-sort-down"
        sort-icon="fa-solid fa-sort"
        :fixed-header="true"
        height="min-content"
      >
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
import { authStore, popupStore } from '@/main'
import { ref } from 'vue'

const challengeData = ref<any[]>([])
const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)
const itemsPerPage = 10
const currentPage = ref<number>(1)
const totalPages = ref<number>(1)

type OrderByParam = 'rank_asc' | 'rank_desc' | 'creator_asc' | 'creator_desc'

function getOrderByParam(
  sortBy: { key: string; order: 'asc' | 'desc' } | null,
): OrderByParam | null {
  // TODO:
  // if (!sortBy) return null
  // switch (sortBy.key) {
  //   case 'rank':
  //     return sortBy.order === 'asc' ? 'rank_asc' : 'rank_desc'
  //   case 'author':
  //     return sortBy.order === 'asc' ? 'creator_asc' : 'creator_desc'
  //   default:
  //     return null
  // }
  return null
}

async function fetchPaginatedData(
  page: number,
  itemsPerPage: number,
  orderBy: OrderByParam | null = null,
) {
  // TODO:
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
