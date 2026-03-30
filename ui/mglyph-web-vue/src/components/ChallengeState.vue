<template>
  <div
    class="challenge-state"
    :class="
      props.state === ChallengeStateEnum.open
        ? 'open'
        : props.state === ChallengeStateEnum.progress
          ? 'progress'
          : 'finished'
    "
  >
    {{ props.state }}
  </div>
</template>

<script lang="ts" setup>
import { ChallengeStateEnum } from '@/services/types'

interface Props {
  state: ChallengeStateEnum
}

const props = defineProps<Props>()
</script>

<style lang="css">
.challenge-state {
  padding: 5px 10px;
  border-radius: 5px;
  width: max-content;
  height: fit-content;
  font-weight: bold;

  &.open {
    background-color: var(--md-extended-color-state-color-1, #05c793);
    color: var(--md-extended-color-on-state-color-1, #ffffff);
  }

  &.progress {
    background-color: var(--md-extended-color-state-color-2, #f64a8a);
    color: var(--md-extended-color-on-state-color-2, #ffffff);
  }

  &.finished {
    background-color: var(--md-extended-color-state-color-3, #2742ba);
    color: var(--md-extended-color-on-state-color-3, #ffffff);
  }
}
</style>
