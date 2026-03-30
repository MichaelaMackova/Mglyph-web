<template>
  <div class="challenge-info">
    <h3>
      <RouterLink :to="{ name: 'ChallengeDetail', params: { id: props.id } }">{{
        props.title
      }}</RouterLink>
    </h3>
    <div class="content">
      <div class="date">
        <span>{{
          props.start_time.toLocaleString([], { dateStyle: 'long', timeStyle: undefined })
        }}</span>
        -
        <span>{{
          props.end_time.toLocaleString([], { dateStyle: 'long', timeStyle: undefined })
        }}</span>
      </div>
      <div
        v-show="props.state !== ChallengeStateEnum.open && props.challengeGlyphs.length > 0"
        class="results-container"
      >
        <ChallengeTable :glyphs="props.challengeGlyphs" />
      </div>
    </div>

    <div class="state-and-user-info">
      <SolverIcon
        v-show="props.user_solver_relationship && props.user_solver_relationship !== 'none'"
      />
      <EvaluatorIcon
        v-show="props.user_evaluator_relationship && props.user_evaluator_relationship !== 'none'"
      />
      <ChallengeState :state="props.state" />
    </div>
  </div>
</template>

<script setup lang="ts">
import ChallengeState from '@/components/ChallengeState.vue'
import ChallengeTable from '@/components/ChallengeTable.vue'
import SolverIcon from '@/components/SolverIcon.vue'
import EvaluatorIcon from '@/components/EvaluatorIcon.vue'
import { ChallengeStateEnum, ChallengeGlyph } from '@/services/types'
import type { UUID } from 'crypto'

interface Props {
  id: UUID
  title: string
  state: ChallengeStateEnum
  start_time: Date
  end_time: Date
  user_solver_relationship?: 'none' | 'registered' | 'mglyph_submitted'
  user_evaluator_relationship?:
    | 'none'
    | 'registered'
    | 'evaluation_awaiting'
    | 'evaluation_finished'
  challengeGlyphs?: ChallengeGlyph[]
}

const props = withDefaults(defineProps<Props>(), {
  id: '00000000-0000-0000-0000-000000000000',
  title: 'Challenge Title',
  state: ChallengeStateEnum.open,
  start_time: () => {
    return new Date()
  },
  end_time: () => {
    const date = new Date()
    date.setMonth(date.getMonth() + 1)
    return date
  },
  challengeGlyphs: () => [],
})
</script>

<style lang="css" scoped>
.state-and-user-info {
  position: absolute;
  right: 0;
  top: 0;

  display: flex;
  gap: 8px;
  align-items: center;

  i {
    font-size: 130%;
  }
}

.challenge-info {
  position: relative;
  width: 100%;

  h3 {
    margin: 0;
  }

  a {
    text-decoration: none;
    color: inherit;
  }
}

.content {
  padding: 0 5px;

  & > * {
    padding-top: 8px;
  }
}

.date {
  font-size: 85%;
}
</style>
