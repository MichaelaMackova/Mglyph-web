<template>
  <v-data-table-server
    :items="props.challengeEvaluators || []"
    :items-length="props.itemsPerPage"
    :headers="headers"
    :items-per-page="props.itemsPerPage"
    :loading="props.isLoading"
    :loading-text="loadingText || 'Loading items...'"
    :no-data-text="
      props.noDataText ||
      (errorOccurred ? 'An error occurred while fetching data.' : 'No data available.')
    "
    :multi-sort="true"
    @update:options="props.onUpdateTableOrder"
    sort-asc-icon="fa-solid fa-sort-up"
    sort-desc-icon="fa-solid fa-sort-down"
    sort-icon="fa-solid fa-sort"
    :fixed-header="true"
    height="min-content"
  >
    <template v-for="(_, slotName) in $slots" v-slot:[`item.${slotName}`]="slotProps">
      <slot :name="slotName" v-bind="slotProps"></slot>
    </template>

    <template v-slot:item.type="{ item }">
      {{ item.invitation_type }}
    </template>

    <template v-slot:item.state="{ item }">
      {{ item.invitation_state }}
    </template>

    <template v-slot:item.actions="{ item }">
      <div class="actions-container" v-if="checkIsActionVisible(item)">
        <button
          class="action-button confirm"
          @click="props.onConfirm(item)"
          :disabled="props.checkActionIsDisabled(item)"
        >
          <div class="label-with-icon">
            <span>Confirm</span>
            <span class="icon">
              <i class="fa-solid fa-check"></i>
            </span>
          </div>
        </button>
        <button
          class="action-button reject"
          @click="props.onReject(item)"
          :disabled="props.checkActionIsDisabled(item)"
        >
          <div class="label-with-icon">
            <span>Reject</span>
            <span class="icon">
              <i class="fa-solid fa-times"></i>
            </span>
          </div>
        </button>
      </div>
    </template>

    <template v-slot:bottom>
      <v-pagination
        :model-value="props.currentPage"
        @update:model-value="props.onChangePage"
        :length="props.totalPages"
        :total-visible="5"
        next-icon="fa-solid fa-caret-right"
        prev-icon="fa-solid fa-caret-left"
      ></v-pagination>
    </template>
  </v-data-table-server>
</template>

<script
  lang="ts"
  setup
  generic="
    ChallengeEvaluator extends {
      id: UUID
      invitation_state: InvitationStateEnum
      invitation_type: InvitationTypeEnum
    }
  "
>
import { InvitationStateEnum, InvitationTypeEnum } from '@/services/types'
import { ref } from 'vue'
import type { UUID } from 'crypto'

interface Props {
  challengeEvaluators: ChallengeEvaluator[]
  onUpdateTableOrder: (options: {
    page: number
    itemsPerPage: number
    sortBy: { key: string; order: 'asc' | 'desc' }[]
  }) => void
  onChangePage: (newPage: number) => void
  currentPage: number
  itemsPerPage: number
  totalPages: number
  noDataText?: string
  loadingText?: string
  isLoading?: boolean
  errorOccurred?: boolean

  checkIsActionVisible?: (item: ChallengeEvaluator) => boolean
  onConfirm?: (item: ChallengeEvaluator) => Promise<void> | void
  onReject?: (item: ChallengeEvaluator) => Promise<void> | void
  checkActionIsDisabled?: (item: ChallengeEvaluator) => boolean

  extraHeaders?: { title: string; key: string; sortable?: boolean }[]
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  errorOccurred: false,
  checkIsActionVisible: () => true,
  onConfirm: () => {},
  onReject: () => {},
  checkActionIsDisabled: () => false,
  extraHeaders: () => [],
})

const headers = ref([
  ...(props.extraHeaders || []),
  { title: 'Invitation Type', key: 'type' },
  { title: 'Invitation State', key: 'state' },
  { title: 'Actions', key: 'actions', sortable: false },
])
</script>

<style lang="css" scoped>
.actions-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

.action-button {
  padding: 5px 10px;
  border-radius: 6px;
  cursor: pointer;

  background-color: rgb(var(--md-sys-color-tertiary-container, 157, 213, 230));
  color: rgb(var(--md-sys-color-on-tertiary-container, 0, 39, 51));
  border: rgba(var(--md-sys-color-on-tertiary-container, 0, 39, 51), 0.2) 1px solid;

  &.confirm:hover:not(:disabled) {
    background-color: rgb(var(--md-sys-color-success, 46, 125, 50));
    color: rgb(var(--md-sys-color-on-success, 255, 255, 255));
  }

  &.reject:hover:not(:disabled) {
    background-color: rgb(var(--md-sys-color-error, 244, 67, 54));
    color: rgb(var(--md-sys-color-on-error, 255, 255, 255));
  }

  &:disabled {
    cursor: not-allowed;
    -webkit-filter: grayscale(1);
    opacity: 0.7;
  }
}

.label-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;

  .icon {
    display: flex;
    align-items: center;
  }
}

/* == table styles == */

.v-table {
  &::v-deep(th) {
    background-color: color-mix(
      in srgb,
      rgb(var(--md-sys-color-outline, 103, 99, 94)) 25%,
      rgb(var(--md-sys-color-surface, 255, 248, 244))
    );
    font-weight: bold;
  }
}

/* ================== */
</style>
