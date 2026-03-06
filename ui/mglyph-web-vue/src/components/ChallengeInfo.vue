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
      <div v-show="props.state !== ChallengeStateEnum.open" class="results-container">
        <ChallengeTable :glyphs="challengeGlyphs" />
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
})

const challengeGlyphs = ref<ChallengeGlyph[]>([
  new ChallengeGlyph(
    'UUID-UUID-UUID-UUID-UUID',
    1,
    { id: 'UUID-UUID-UUID-UUID-1234', username: 'JohnHan' },
    ['flag1', 'flag2'],
  ),
  new ChallengeGlyph(
    'UUID-UUID-UUID-UUID-UUID2',
    2,
    { id: 'UUID-UUID-UUID-UUID-0000', username: 'JaneDoe' },
    ['flag3'],
  ),
])
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
