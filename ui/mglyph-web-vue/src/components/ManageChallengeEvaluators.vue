<template>
  <div class="manage-challenge-evaluators-component">
    <h3>Invite New Evaluators</h3>
    <div class="selection-container">
      <v-autocomplete
        v-model="selectedItems"
        v-model:search="search"
        @update:search="onSearchInput"
        :items="fetchedUsers || []"
        :loading="loading"
        return-object
        label="Select New Evaluators"
        placeholder="useremail@example.com"
        :no-data-text="search ? 'No users found' : 'Start typing to search users'"
        autocomplete="off"
        no-filter
        clear-on-select
        chips
        closable-chips
        multiple
        hide-details
      >
        <template v-slot:chip="{ props, item }">
          <v-chip
            v-bind="props"
            :text="item.username"
            close-icon="fa-solid fa-circle-xmark"
          ></v-chip>
        </template>

        <template v-slot:item="{ props, item }">
          <div title="disabled">
            <v-list-item v-bind="props" :title="item.username" :disabled="false"></v-list-item>
          </div>
        </template>
      </v-autocomplete>
      <button class="invite-button" @click="onInvite" :disabled="isInviting">
        <div v-if="!isInviting" class="label-with-icon">
          <span class="label">Invite Evaluators</span>
        </div>
        <div v-else class="label-with-icon">
          <span class="label">Sending invites...</span>
          <span class="icon"><i class="fa-solid fa-spinner fa-spin-pulse"></i></span>
        </div>
      </button>
    </div>

    <h3>Manage Invites</h3>
    <ChallengeEvaluatorTableBase
      :challengeEvaluators="challengeEvaluatorsTable || []"
      :isLoading="isTableLoading"
      :errorOccurred="errorOccurredTable"
      :onUpdateTableOrder="
        ({ page, itemsPerPage, sortBy }) => {
          currentTablePage = 1
          currentOrderBy = getOrderByParam(sortBy)
          fetchChallengeEvaluators(page, itemsPerPage, currentOrderBy)
        }
      "
      :onChangePage="
        (page) => {
          currentTablePage = page
          fetchChallengeEvaluators(page, itemsPerTablePage, currentOrderBy)
        }
      "
      :currentPage="currentTablePage"
      :itemsPerPage="itemsPerTablePage"
      :totalPages="totalTablePages"
      :noDataText="
        errorOccurredTable
          ? 'An error occurred while fetching evaluator data.'
          : 'No evaluators found.'
      "
      :loadingText="'Loading evaluators...'"
      :extraHeaders="[{ title: 'Username', key: 'username' }]"
      :checkIsActionVisible="
        (item) =>
          item.invitation_state === InvitationStateEnum.pending &&
          item.invitation_type === InvitationTypeEnum.volunteer
      "
      :onConfirm="confirmAction"
      :onReject="rejectAction"
    >
      <template v-slot:username="{ item }"> {{ item.evaluator.username }} </template>
    </ChallengeEvaluatorTableBase>
  </div>
</template>

<script lang="ts" setup>
import ChallengeEvaluatorTableBase from '@/components/ChallengeEvaluatorTableBase.vue'
import {
  User,
  ChallengeEvaluatorInfoWithEvaluator,
  PaginatedData,
  InvitationStateEnum,
  InvitationTypeEnum,
} from '@/services/types'
import { debounce } from '@/services/debounce'
import { mglyphClient } from '@/clients/mglyph_client'
import { authStore, popupStore } from '@/main'
import { ref, watch } from 'vue'
import type { UUID } from 'crypto'

interface Props {
  challengeId: UUID
}

const props = defineProps<Props>()

/* ========== Select and Invite Evaluators ========== */
const search = ref<string>('')
const selectedItems = ref<User[]>([])
const fetchedUsers = ref<User[] | null>(null)
const loading = ref<boolean>(false)
const isInviting = ref<boolean>(false)
const numberOfFetchedUsers = 10

async function fetchUsers(searchTerm: string) {
  // EXTENSION: get participation info for each user (e.g. is the user already an evaluator for the challenge)
  loading.value = true
  try {
    const response = await mglyphClient.get('/users', {
      authorizeEndpoint: false,
      params: {
        username_contains: searchTerm !== '' ? searchTerm : null,
        size: numberOfFetchedUsers,
        page: 1,
      },
    })
    fetchedUsers.value = response.data.items.map((user: any) => new User(user.id, user.username))
  } catch (err) {
    console.error('Failed to fetch users:', err)
  } finally {
    loading.value = false
  }
}

let debouncedFetchUsers = debounce(fetchUsers, 500)

function onSearchInput(newSearchValue: string) {
  loading.value = true
  debouncedFetchUsers(newSearchValue)
}

async function onInvite() {
  if (selectedItems.value.length === 0) return

  isInviting.value = true
  for (const user of selectedItems.value) {
    try {
      await mglyphClient.post(
        `/challenges/${props.challengeId}/invite-evaluator`,
        {},
        {
          authorizeEndpoint: true,
          params: {
            evaluator_user_id: user.id,
          },
        },
      )
    } catch (err) {
      console.error('Failed to send invitation:', err)
      popupStore.addPopup(
        'Failed to send invitation to ' + user.username,
        popupStore.PopupTypeEnum.error,
      )
    }
  }
  selectedItems.value = []
  fetchChallengeEvaluators(currentTablePage.value, itemsPerTablePage, currentOrderBy.value)
  isInviting.value = false
}
/* ========== End of Select and Invite Evaluators ========== */

/* ========== Table Actions ========== */
const isTableLoading = ref<boolean>(false)
const errorOccurredTable = ref<boolean>(false)
const currentTablePage = ref<number>(1)
const itemsPerTablePage = 10
const totalTablePages = ref<number>(1)
const challengeEvaluatorsTable = ref<ChallengeEvaluatorInfoWithEvaluator[] | null>(null)

type OrderByParam =
  | 'evaluator_username_asc'
  | 'evaluator_username_desc'
  | 'invitation_type_asc'
  | 'invitation_type_desc'
  | 'invitation_state_asc'
  | 'invitation_state_desc'

const currentOrderBy = ref<OrderByParam[] | null>(null)

function getOrderByParam(
  sortBy: { key: string; order: 'asc' | 'desc' }[] | null,
): OrderByParam[] | null {
  if (!sortBy || sortBy.length === 0) return null
  return sortBy
    .map((sort) => {
      switch (sort.key) {
        case 'type':
          return sort.order === 'asc' ? 'invitation_type_asc' : 'invitation_type_desc'
        case 'state':
          return sort.order === 'asc' ? 'invitation_state_asc' : 'invitation_state_desc'
        case 'username':
          return sort.order === 'asc' ? 'evaluator_username_asc' : 'evaluator_username_desc'
        default:
          return null
      }
    })
    .filter((param): param is OrderByParam => param !== null)
}

async function fetchChallengeEvaluators(
  page: number,
  itemsPerPage: number,
  orderBy: OrderByParam[] | null = null,
) {
  isTableLoading.value = true
  errorOccurredTable.value = false
  try {
    const response = await mglyphClient.get(`/challenges/${props.challengeId}/evaluators`, {
      authorizeEndpoint: true,
      params: {
        page: page,
        size: itemsPerPage,
        order_by: orderBy,
      },
    })
    const paginatedEvaluators = PaginatedData.fromAPIResponse(
      response.data,
      ChallengeEvaluatorInfoWithEvaluator.fromAPIResponse,
    )
    challengeEvaluatorsTable.value = paginatedEvaluators.items
    totalTablePages.value = paginatedEvaluators.total_pages
    currentTablePage.value = paginatedEvaluators.current_page
  } catch (error) {
    errorOccurredTable.value = true
    console.error('Error fetching challenge evaluators:', error)
    popupStore.addPopup(
      'Failed to load evaluator invites. Please try again later.',
      popupStore.PopupTypeEnum.error,
    )
  } finally {
    isTableLoading.value = false
  }
}

async function confirmAction(item: ChallengeEvaluatorInfoWithEvaluator) {
  isTableLoading.value = true
  try {
    await mglyphClient.post(
      `/challenges/${props.challengeId}/confirm-volunteer-evaluator/${item.evaluator.id}`,
      {},
      { authorizeEndpoint: true },
    )
    await fetchChallengeEvaluators(currentTablePage.value, itemsPerTablePage, currentOrderBy.value)
  } catch (error) {
    console.error('Error confirming action:', error)
    popupStore.addPopup(
      'Failed to confirm invite. Please try again.',
      popupStore.PopupTypeEnum.error,
    )
  } finally {
    isTableLoading.value = false
  }
}

async function rejectAction(item: ChallengeEvaluatorInfoWithEvaluator) {
  isTableLoading.value = true
  try {
    await mglyphClient.post(
      `/challenges/${props.challengeId}/reject-volunteer-evaluator/${item.evaluator.id}`,
      {},
      { authorizeEndpoint: true },
    )
    await fetchChallengeEvaluators(currentTablePage.value, itemsPerTablePage, currentOrderBy.value)
  } catch (error) {
    console.error('Error rejecting action:', error)
    popupStore.addPopup(
      'Failed to reject invite. Please try again.',
      popupStore.PopupTypeEnum.error,
    )
  } finally {
    isTableLoading.value = false
  }
}
/* ========== End of Table Actions ========== */
</script>

<style lang="css" scoped>
.label-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;

  .icon {
    display: flex;
    align-items: center;
  }
}

.selection-container {
  width: 60vw;
  max-width: 750px;
  margin: 20px auto;
}

.invite-button {
  display: block;
  margin: 10px auto;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;

  background-color: rgb(var(--md-sys-color-tertiary, 0, 129, 167));
  color: rgb(var(--md-sys-color-on-tertiary, 255, 255, 255));

  &:disabled {
    cursor: not-allowed;
    -webkit-filter: grayscale(1);
    opacity: 0.5;
  }
}
</style>

<style lang="css">
.v-overlay .v-list {
  --v-theme-surface: var(--md-sys-color-surface, 255, 248, 244);
  --v-theme-on-surface: var(--md-sys-color-on-surface, 32, 27, 19);

  .v-list-item::after {
    border-width: 0;
  }
}
</style>
