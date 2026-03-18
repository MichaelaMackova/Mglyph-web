<template>
  <div class="challenge-info">
    <h3>{{ props.title }}</h3>
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
    <ChallengeState :state="props.state" />
  </div>
</template>

<script setup lang="ts">
import ChallengeState from '@/components/ChallengeState.vue'
import ChallengeTable from '@/components/ChallengeTable.vue'
import { ChallengeStateEnum, ChallengeGlyph } from '@/services/types'
import { ref } from 'vue'

interface Props {
  title: string
  state: ChallengeStateEnum
  start_time: Date
  end_time: Date
  challengeGlyphs?: ChallengeGlyph[]
}

const props = withDefaults(defineProps<Props>(), {
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

<style lang="css">
.challenge-state {
  position: absolute;
  right: 0;
  top: 0;
}
</style>

<style lang="css" scoped>
.challenge-info {
  position: relative;
  width: 100%;

  h3 {
    margin: 0;
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
