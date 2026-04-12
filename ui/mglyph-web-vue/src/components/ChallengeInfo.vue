<template>
  <div class="challenge-info">
    <h3>
      <RouterLink :to="{ name: 'ChallengeDetail', params: { id: props.id } }">{{
        props.title
      }}</RouterLink>
    </h3>
    <div class="content">
      <div class="date">
        <span>{{ formatDate(props.start_time) }}</span>
        -
        <span>{{ formatDate(props.submission_deadline) }}</span>
        -
        <span>{{ formatDate(props.end_time) }}</span>
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
      <EvaluatorIcon v-show="isActiveEvaluator()" />
      <ChallengeState :state="props.state" />
    </div>
  </div>
</template>

<script setup lang="ts">
import ChallengeState from '@/components/ChallengeState.vue'
import ChallengeTable from '@/components/ChallengeTable.vue'
import SolverIcon from '@/components/icons/SolverIcon.vue'
import EvaluatorIcon from '@/components/icons/EvaluatorIcon.vue'
import {
  ChallengeStateEnum,
  ChallengeGlyph,
  ChallengeUserSolverRelationshipType,
  ChallengeUserEvaluatorRelationshipType,
} from '@/services/types'
import type { UUID } from 'crypto'

interface Props {
  id: UUID
  title: string
  state: ChallengeStateEnum
  start_time: Date
  submission_deadline: Date
  end_time: Date
  user_solver_relationship?: ChallengeUserSolverRelationshipType
  user_evaluator_relationship?: ChallengeUserEvaluatorRelationshipType
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

function formatDate(date: Date): string {
  return date.toLocaleString([], { dateStyle: 'long', timeStyle: undefined })
}

function isActiveEvaluator(): boolean {
  return (
    (props.user_evaluator_relationship &&
      (props.user_evaluator_relationship === ChallengeUserEvaluatorRelationshipType.registered ||
        props.user_evaluator_relationship ===
          ChallengeUserEvaluatorRelationshipType.evaluation_awaiting ||
        props.user_evaluator_relationship ===
          ChallengeUserEvaluatorRelationshipType.evaluation_finished)) ||
    false
  )
}
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
