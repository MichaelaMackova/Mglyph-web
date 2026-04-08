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
    background-color: rgb(var(--md-extended-color-state-color-1, 5, 199, 147));
    color: rgb(var(--md-extended-color-on-state-color-1, 255, 255, 255));
  }

  &.progress {
    background-color: rgb(var(--md-extended-color-state-color-2, 246, 74, 138));
    color: rgb(var(--md-extended-color-on-state-color-2, 255, 255, 255));
  }

  &.finished {
    background-color: rgb(var(--md-extended-color-state-color-3, 39, 66, 186));
    color: rgb(var(--md-extended-color-on-state-color-3, 255, 255, 255));
  }
}
</style>
