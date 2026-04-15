<template>
  <div class="main-padding">
    <h1>Managing My Evaluator Invites and Requests</h1>
    <div v-if="!authStore.user">
      <PopupNote
        message="Please login to view your challenges"
        type="error"
        width="max-content"
        :closable="false"
      />
    </div>
    <div v-else>
      <!-- My invites content goes here -->
      <ChallengeEvaluatorTableBase
        :challengeEvaluators="challengeEvaluators || []"
        :isLoading="isLoading"
        :errorOccurred="errorOccurred"
        :onUpdateTableOrder="
          ({ page, itemsPerPage, sortBy }) => {
            currentPage = 1
            currentOrderBy = getOrderByParam(sortBy)
            fetchChallengeEvaluators(page, itemsPerPage, currentOrderBy)
          }
        "
        :onChangePage="
          (page) => {
            currentPage = page
            fetchChallengeEvaluators(page, itemsPerPage, currentOrderBy)
          }
        "
        :currentPage="currentPage"
        :itemsPerPage="itemsPerPage"
        :totalPages="totalPages"
        :extraHeaders="[{ title: 'Challenge Name', key: 'ch_name' }]"
        :onConfirm="confirmAction"
        :onReject="rejectAction"
        :checkActionIsDisabled="(item) => item.challenge.state === ChallengeStateEnum.finished"
      >
        <template v-slot:ch_name="{ item }">
          <RouterLink :to="{ name: 'ChallengeDetail', params: { id: item.challenge.id } }">
            {{ item.challenge.title }}
          </RouterLink>
        </template>
      </ChallengeEvaluatorTableBase>
    </div>
  </div>
</template>

<script lang="ts" setup>
import PopupNote from '@/components/PopupNote.vue'
import ChallengeEvaluatorTableBase from '@/components/ChallengeEvaluatorTableBase.vue'
import {
  ChallengeEvaluatorInfoWithChallenge,
  PaginatedData,
  ChallengeStateEnum,
} from '@/services/types'
import { authStore, popupStore } from '@/main'
import { mglyphClient } from '@/clients/mglyph_client'
import { ref } from 'vue'

const isLoading = ref<boolean>(false)
const errorOccurred = ref<boolean>(false)
const currentPage = ref<number>(1)
const itemsPerPage = 10
const totalPages = ref<number>(1)
const challengeEvaluators = ref<ChallengeEvaluatorInfoWithChallenge[] | null>(null)

type OrderByParam =
  | 'challenge_name_asc'
  | 'challenge_name_desc'
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
        case 'ch_name':
          return sort.order === 'asc' ? 'challenge_name_asc' : 'challenge_name_desc'
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
  isLoading.value = true
  errorOccurred.value = false

  try {
    const response = await mglyphClient.get(`/challenges/my-evaluator-invites`, {
      authorizeEndpoint: true,
      params: {
        page: page,
        size: itemsPerPage,
        order_by: orderBy,
      },
    })
    const paginatedEvaluators = PaginatedData.fromAPIResponse(
      response.data,
      ChallengeEvaluatorInfoWithChallenge.fromAPIResponse,
    )
    challengeEvaluators.value = paginatedEvaluators.items
    totalPages.value = paginatedEvaluators.total_pages
    currentPage.value = paginatedEvaluators.current_page
  } catch (error) {
    errorOccurred.value = true
    console.error('Error fetching challenge evaluators:', error)
    popupStore.addPopup(
      'Failed to load your evaluator invites. Please try again later.',
      popupStore.PopupTypeEnum.error,
    )
  } finally {
    isLoading.value = false
  }
}

async function reloadComponent() {
  isLoading.value = true
  errorOccurred.value = false
  challengeEvaluators.value = null
  await fetchChallengeEvaluators(currentPage.value, itemsPerPage, currentOrderBy.value)
}

async function confirmAction(item: ChallengeEvaluatorInfoWithChallenge) {
  isLoading.value = true
  try {
    await mglyphClient.post(
      `/challenges/${item.challenge.id}/confirm-evaluator-invite`,
      {},
      { authorizeEndpoint: true },
    )
    await fetchChallengeEvaluators(currentPage.value, itemsPerPage, currentOrderBy.value)
  } catch (error) {
    console.error('Error confirming action:', error)
    popupStore.addPopup(
      'Failed to confirm invite. Please try again.',
      popupStore.PopupTypeEnum.error,
    )
  } finally {
    isLoading.value = false
  }
}

async function rejectAction(item: ChallengeEvaluatorInfoWithChallenge) {
  isLoading.value = true
  try {
    await mglyphClient.post(
      `/challenges/${item.challenge.id}/reject-evaluator-invite`,
      {},
      { authorizeEndpoint: true },
    )
    await fetchChallengeEvaluators(currentPage.value, itemsPerPage, currentOrderBy.value)
  } catch (error) {
    console.error('Error rejecting action:', error)
    popupStore.addPopup(
      'Failed to reject invite. Please try again.',
      popupStore.PopupTypeEnum.error,
    )
  } finally {
    isLoading.value = false
  }
}
</script>

<style lang="css" scoped></style>
