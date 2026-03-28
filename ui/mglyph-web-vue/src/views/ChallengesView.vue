<template>
  <div class="main-padding">
    <h1>Challenges</h1>
  </div>

  <div class="filters main-padding">
    <FilterList :options="filters" />
  </div>

  <div class="challenges-container">
    <div v-if="isLoading || errorOccurred" class="main-padding">
      <p v-if="isLoading">
        Loading challenges... <i class="fa-solid fa-spinner fa-spin-pulse"></i>
      </p>
      <p v-else-if="errorOccurred">An error occurred while fetching challenges.</p>
    </div>
    <div v-else-if="responseData?.challenges.length === 0" class="main-padding">
      <p>No challenges available.</p>
    </div>
    <div
      v-else
      class="challenge-info-container main-padding"
      v-for="challenge_info in responseData?.challenges"
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

    <v-pagination
      v-model="currentPage"
      @update:model-value="pushNewRoute"
      :length="responseData?.total_pages || 1"
      :total-visible="5"
      next-icon="fa-solid fa-caret-right"
      prev-icon="fa-solid fa-caret-left"
    ></v-pagination>
  </div>
</template>

<script setup lang="ts">
import ChallengeInfo from '@/components/ChallengeInfo.vue'
import FilterList from '@/components/FilterList.vue'
import { mglyphClient } from '@/clients/mglyph_client'
import { ref, watch } from 'vue'
import { ChallengeStateEnum, ChallengeSimple, ChallengeGlyph, User } from '@/services/types'
import { authStore } from '@/main'
import { useRouter, type LocationQuery } from 'vue-router'
const router = useRouter()

const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)
const responseData = ref<{
  challenges: {
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
  total_count: number
  total_pages: number
  current_page: number
  page_size: number
} | null>(null)
const currentPage = ref<number>(1)
const filters = ref<FilterList.FilterOption[]>([
  { label: 'All', selected: true, onClick: () => onClickFilter(0) },
  { label: 'Open', selected: false, onClick: () => onClickFilter(1) },
  { label: 'Evaluating', selected: false, onClick: () => onClickFilter(2) },
  { label: 'Finished', selected: false, onClick: () => onClickFilter(3) },
])

async function fetchChallenges(page: number) {
  // isLoading.value = true
  errorOccurred.value = false
  // responseData.value = null
  try {
    let stateFilterArray = []
    if (!filters.value[0].selected) {
      for (let index = 1; index < filters.value.length; index++) {
        const element = filters.value[index]
        if (element.selected) {
          stateFilterArray.push(element.label.toLowerCase())
        }
      }
    }
    const response = await mglyphClient.get('/challenges', {
      authorizeEndpoint: authStore.user ? true : false,
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
    responseData.value = {
      challenges: response.data.items.map((challenge: any) => {
        var ch = new ChallengeSimple(
          challenge.id,
          challenge.name,
          new Date(2021, 0, 1), // TODO: Replace with actual start time from response
          new Date(challenge.glyph_submit_deadline), // TODO: Replace with actual end time from response
          challenge.state,
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
      }),
      total_count: response.data.total,
      total_pages: response.data.total_pages,
      current_page: response.data.page,
      page_size: response.data.size,
    }
  } catch (err) {
    console.error(err)
    errorOccurred.value = true
  } finally {
    isLoading.value = false
  }
}

function onClickFilter(option_index: number) {
  if (option_index === 0) {
    filters.value[0].selected = true
    for (let index = 1; index < filters.value.length; index++) {
      filters.value[index].selected = false
    }
  } else {
    if (filters.value[option_index].selected) {
      filters.value[option_index].selected = false
      let anyOtherSelected = false
      for (let index = 1; index < filters.value.length; index++) {
        if (filters.value[index].selected) {
          anyOtherSelected = true
          break
        }
      }
      if (!anyOtherSelected) {
        filters.value[0].selected = true
      }
    } else {
      filters.value[option_index].selected = true
      filters.value[0].selected = false
    }
  }
  pushNewRoute()
}

function pushNewRoute(page?: number) {
  let newQuery = { ...router.currentRoute.value.query }
  // Page
  if (page) {
    if (page === 1) {
      delete newQuery.page
    } else {
      newQuery.page = page.toString()
    }
  }

  // Filtering
  if (filters.value[0].selected) {
    delete newQuery.state
  } else {
    const stateValues = filters.value
      .filter((f): f is { label: string } => f.selected)
      .map((f) => f.label.toLowerCase())
    if (stateValues.length > 0) {
      newQuery.state = stateValues.join(',')
    } else {
      delete newQuery.state
    }
  }

  // if (JSON.stringify(newQuery) !== JSON.stringify(router.currentRoute.value.query)) {
  //   router.push({ query: newQuery })
  // }
  router.push({ query: newQuery })
}

function initializePageFromQuery(query: LocationQuery) {
  const pageParam = query.page
  if (pageParam === undefined) {
    currentPage.value = 1
  } else if (typeof pageParam === 'string') {
    const pageNum = parseInt(pageParam, 10)
    if (!isNaN(pageNum) && pageNum > 0) {
      currentPage.value = pageNum
    }
  }
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
      filters.value[0].selected = true
    }
  }
}

watch(
  () => router.currentRoute.value.query,
  (newQuery) => {
    initializePageFromQuery(newQuery)
    initializeFiltersFromQuery(newQuery)
    fetchChallenges(currentPage.value)
  },
  { immediate: true },
)
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

.filters {
  margin-bottom: 10px;
}
</style>
