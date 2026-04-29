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
    <div v-else>
      <div v-if="props.challenges.length === 0" class="main-padding">
        <p>No challenges available.</p>
      </div>
      <div>
        <div v-if="props.showAddNewButton" class="challenge-info-container main-padding">
          <div class="add-new" @click="props.onAddNewButtonClicked">
            <div><i class="fa-solid fa-circle-plus fa-2x"></i></div>
            <div>Add New Challenge</div>
          </div>
        </div>
        <div
          class="challenge-info-container main-padding"
          v-for="challenge_info in props.challenges"
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
import ChallengeInfo from '@/components/ChallengeInfo.vue'
import FilterList from '@/components/FilterList.vue'

interface Props {
  currentPage: number
  totalPages: number
  filters: FilterOption[]
  onUpdatePagination: (page: number) => void
  challenges: ChallengeMiniDetail[]
  isLoading: boolean
  errorOccurred: boolean
  showAddNewButton?: boolean
  onAddNewButtonClicked?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  showAddNewButton: false,
  onAddNewButtonClicked: () => {},
})
</script>

<style lang="css" scoped>
.challenges-container {
  padding-bottom: 20px;
}

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

.add-new {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  cursor: pointer;

  div {
    display: flex;
    justify-content: center;
    align-items: center;
  }
}

.filters {
  margin-bottom: 10px;
}
</style>
