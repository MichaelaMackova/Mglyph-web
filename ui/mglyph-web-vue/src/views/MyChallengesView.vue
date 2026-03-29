<template>
  <div class="main-padding">
    <h1>My Challenges</h1>
  </div>

  <div v-if="!authStore.user" class="main-padding">
    <PopupNote message="Please login to view your challenges" type="error" :closable="false" />
  </div>

  <ChallengeViewTemplate
    v-else
    :currentPage="currentPage"
    :totalPages="responseData?.total_pages || 1"
    :filters="filters"
    :onUpdatePagination="
      (newPage: number) => {
        currentPage = newPage
        pushNewRoute(newPage)
      }
    "
    :challenges="responseData?.items || []"
    :isLoading="isLoading"
    :errorOccurred="errorOccurred"
  />
</template>

<script setup lang="ts">
import ChallengeViewTemplate from '@/components/ChallengeViewTemplate.vue'
import PopupNote from '@/components/PopupNote.vue'
import { ChallengeMiniDetail, PaginatedData, FilterOption } from '@/services/types'
import { mglyphClient } from '@/clients/mglyph_client'
import { authStore } from '@/main'
import { initializePageFromQuery, changePageInQuery } from '@/services/routing-utils'
import { useRouter, type LocationQuery } from 'vue-router'
import { ref, watch } from 'vue'
const router = useRouter()

const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)
const currentPage = ref<number>(1)
const filters = ref<FilterOption[]>([
  new FilterOption('All', true, () => onClickFilter(0)),
  new FilterOption('Open', false, () => onClickFilter(1)),
  new FilterOption('Evaluating', false, () => onClickFilter(2)),
  new FilterOption('Finished', false, () => onClickFilter(3)),
])
const responseData = ref<PaginatedData<ChallengeMiniDetail> | null>(null)

async function fetchChallenges(page: number) {
  isLoading.value = true
  errorOccurred.value = false
  // responseData.value = null
  try {
    let stateFilterArray = []
    if (!filters.value[0]?.selected) {
      for (let index = 1; index < filters.value.length; index++) {
        const element = filters.value[index]
        if (element?.selected) {
          stateFilterArray.push(element.label.toLowerCase())
        }
      }
    }
    const response = await mglyphClient.get('/challenges/user-is-participant', {
      authorizeEndpoint: true,
      params: {
        glyph_count: 3,
        page: page,
        size: 3,
        state: stateFilterArray,
      },
    })
    if (!Array.isArray(response.data.items)) {
      throw new Error('Invalid response format: expected an array')
    }
    responseData.value = new PaginatedData<ChallengeMiniDetail>(
      response.data.items.map((item: any) => ChallengeMiniDetail.fromAPIResponse(item)),
      response.data.total,
      response.data.total_pages,
      response.data.page,
      response.data.size,
    )
  } catch (err) {
    console.error(err)
    errorOccurred.value = true
  } finally {
    isLoading.value = false
  }
}

function onClickFilter(option_index: number) {
  if (option_index === 0) {
    filters.value.forEach((filter, index) => {
      filter.selected = index === 0
    })
  } else {
    if (filters.value[option_index]?.selected) {
      filters.value[option_index].selected = false
      let anyOtherSelected = false
      for (let index = 1; index < filters.value.length; index++) {
        if (filters.value[index]?.selected) {
          anyOtherSelected = true
          break
        }
      }
      if (!anyOtherSelected) {
        filters.value[0]!.selected = true
      }
    } else {
      filters.value[option_index]!.selected = true
      filters.value[0]!.selected = false
    }
  }
  currentPage.value = 1
  pushNewRoute()
}

function pushNewRoute(page?: number) {
  let newQuery = changePageInQuery(router.currentRoute.value.query, page ?? currentPage.value)

  // Filtering
  if (filters.value[0]?.selected) {
    delete newQuery.state
  } else {
    const stateValues = filters.value.filter((f) => f.selected).map((f) => f.label.toLowerCase())
    if (stateValues.length > 0) {
      newQuery.state = stateValues.join(',')
    } else {
      delete newQuery.state
    }
  }

  router.push({ query: newQuery })
}

function initializeFiltersFromQuery(query: LocationQuery) {
  const stateParam = query.state
  if (stateParam === undefined) {
    filters.value.forEach((filter, index) => {
      filter.selected = index === 0
    })
  } else if (typeof stateParam === 'string') {
    const stateValues = stateParam.split(',')
    let isSelected = false
    filters.value.forEach((filter) => {
      filter.selected = stateValues.includes(filter.label.toLowerCase())
      if (filter.selected) {
        isSelected = true
      }
    })
    if (!isSelected) {
      filters.value[0]!.selected = true
    }
  }
}

watch(
  () => router.currentRoute.value.query,
  (newQuery) => {
    currentPage.value = initializePageFromQuery(newQuery)
    initializeFiltersFromQuery(newQuery)
    fetchChallenges(currentPage.value)
  },
  { immediate: true },
)
</script>
