<template>
  <div class="filters main-padding">
    <FilterList :options="props.filters" />
  </div>

  <div class="challenges-container">
    <div v-if="props.isLoading || props.errorOccurred" class="main-padding">
      <p v-if="props.isLoading">
        Loading challenges... <i class="fa-solid fa-spinner fa-spin-pulse"></i>
      </p>
      <p v-else-if="props.errorOccurred">An error occurred while fetching challenges.</p>
    </div>
    <div v-else-if="props.challenges.length === 0" class="main-padding">
      <p>No challenges available.</p>
    </div>
    <div
      v-else
      class="challenge-info-container main-padding"
      v-for="challenge_info in props.challenges"
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
      :model-value="props.currentPage"
      @update:model-value="props.onUpdatePagination"
      :length="props.totalPages || 1"
      :total-visible="5"
      next-icon="fa-solid fa-caret-right"
      prev-icon="fa-solid fa-caret-left"
    ></v-pagination>
  </div>
</template>

<script setup lang="ts">
import { ChallengeMiniDetail, FilterOption } from '@/services/types'
interface Props {
  currentPage: number
  totalPages: number
  filters: FilterOption[]
  onUpdatePagination: (page: number) => void
  challenges: ChallengeMiniDetail[]
  isLoading: boolean
  errorOccurred: boolean
}

const props = defineProps<Props>()

import ChallengeInfo from '@/components/ChallengeInfo.vue'
import FilterList from '@/components/FilterList.vue'
</script>

<style lang="css" scoped>
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
