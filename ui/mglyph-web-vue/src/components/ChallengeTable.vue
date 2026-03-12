<template>
  <table>
    <thead>
      <tr>
        <th class="rank">#</th>
        <th class="author">Author</th>
        <th class="glyph">Glyph</th>
        <th class="flags">Flags</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="glyph in props.glyphs" :key="glyph.id">
        <td>{{ glyph.rank }}</td>
        <td>{{ glyph.author.username }}</td>
        <td>TODO:</td>
        <td>{{ glyph.flags.join(', ') }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import { ChallengeGlyph } from '@/services/types'

interface Props {
  glyphs: ChallengeGlyph[]
}

const props = withDefaults(defineProps<Props>(), {
  glyphs: () => [],
})
</script>

<style lang="css" scoped>
table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;

  th,
  td {
    padding: 3px 8px;
    border: 1px solid var(--md-sys-color-outline, #67635e);
  }
}

th {
  background-color: color-mix(in srgb, var(--md-sys-color-outline, #67635e) 25%, transparent);

  &.rank {
    width: 60px;
  }

  &.author {
    min-width: 250px;
    width: 30%;
  }

  &.glyph {
    width: auto;
  }

  &.flags {
    width: 100px;
  }
}
</style>
