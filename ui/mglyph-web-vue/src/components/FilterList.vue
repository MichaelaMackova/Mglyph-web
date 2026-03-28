<template>
  <ul>
    <li
      v-for="option in props.options"
      :key="option.label"
      @click="option.onClick"
      :class="option.selected ? 'selected' : ''"
    >
      {{ option.label }}
      <i class="fa-solid fa-check" v-if="option.selected"></i>
    </li>
  </ul>
</template>

<script setup lang="ts">
class FilterOption {
  label: string
  selected: boolean
  onClick: () => void

  constructor(label: string, selected: boolean = false, onClick: () => void = () => {}) {
    this.label = label
    this.onClick = onClick
    this.selected = selected
  }
}

interface Props {
  options: FilterOption[]
}

const props = withDefaults(defineProps<Props>(), {
  options: () => [],
})
</script>

<style scoped lang="css">
ul {
  list-style-type: none;
  margin: 0;
  padding: 0;

  display: flex;
  gap: 3px;
}

li {
  padding: 5px 10px;
  align-content: center;
  border-radius: 8px;
  border: 1px solid color-mix(in srgb, var(--md-sys-color-outline, #67635e) 25%, transparent);
  background: var(--md-sys-color-secondary, #00afb9);
  color: var(--md-sys-color-on-secondary, #ffffff);

  &:hover {
    cursor: pointer;
  }

  &.selected {
    background: var(--md-sys-color-secondary-container, #9de2e6);
    color: var(--md-sys-color-on-secondary-container, #003033);
  }
}
</style>
