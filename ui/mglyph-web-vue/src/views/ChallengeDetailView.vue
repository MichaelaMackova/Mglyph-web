<template>
  <div class="main-padding">
    <div v-if="isLoading" class="main-top-margin">
      Loading challenge data... <i class="fa-solid fa-spinner fa-spin-pulse"></i>
    </div>
    <div v-else-if="errorOccurred || !challengeData" class="main-top-margin">
      <PopupNote
        message="An error occurred while fetching challenge data. Please try again later."
        type="error"
        :closable="false"
        width="max-content"
      />
    </div>
    <div v-else>
      <div class="title-and-state">
        <h1>{{ challengeData.challenge.title }}</h1>

        <div class="state-and-user-info">
          <ChallengeState :state="challengeData.challenge.state" />
          <div class="user-info">
            <SolverIcon v-show="isUserSolver()" />
            <EvaluatorIcon v-show="isActiveUserEvaluator()" />
          </div>
        </div>
      </div>

      <div class="info-piece">
        <span class="label">Created:</span>
        {{
          challengeData.challenge.start_time.toLocaleString([], {
            dateStyle: 'long',
            timeStyle: 'short',
          })
        }}
      </div>
      <div class="info-piece">
        <span class="label">Submissions deadline:</span>
        {{
          challengeData.challenge.submission_deadline.toLocaleString([], {
            dateStyle: 'long',
            timeStyle: 'short',
          })
        }}
      </div>
      <div class="info-piece">
        <span class="label">Evaluations estimated until:</span>
        {{
          challengeData.challenge.evaluation_deadline.toLocaleString([], {
            dateStyle: 'long',
            timeStyle: 'short',
          })
        }}
      </div>

      <div
        v-if="authStore.user && challengeData.challenge.state !== ChallengeStateEnum.finished"
        class="buttons-container"
      >
        <div v-if="authStore.user.role === 'admin'">
          <button
            class="admin-button"
            v-if="challengeData.challenge.state === ChallengeStateEnum.open"
            @click="onEndSubmissionsClick"
          >
            End Submissions
          </button>
          <button
            class="admin-button"
            v-if="challengeData.challenge.state === ChallengeStateEnum.progress"
            @click="onEndChallengeClick"
          >
            End Challenge
          </button>
        </div>
        <div class="user-buttons-container">
          <button
            v-if="challengeData.challenge.state === ChallengeStateEnum.open && !isUserSolver()"
            class="user-button"
            @click="onParticipantSignUpClick"
          >
            <div class="label-with-icon">
              <span class="label">Sign Up As Participant</span>
              <span class="icon"><SolverIcon /></span>
            </div>
          </button>
          <button
            v-if="
              challengeData.challenge.state === ChallengeStateEnum.open &&
              challengeData.user_relationship!.user_solver_relationship! ===
                ChallengeUserSolverRelationshipType.registered
            "
            class="user-button"
            @click="onUploadGlyphClick"
          >
            <div class="label-with-icon">
              <span class="label">Upload My Malleable Glyph</span>
              <span class="icon"><i class="fa-solid fa-upload"></i></span>
            </div>
          </button>
          <!-- TODO: check if it works properly and find glyph -->
          <!-- <button
              v-if="
              challengeData.challenge.state === ChallengeStateEnum.open &&
                challengeData.user_relationship!.user_solver_relationship! ===
                ChallengeUserSolverRelationshipType.mglyph_submitted
              "
              class="user-button"
            >
              Show My Malleable Glyph
            </button> -->
          <button
            v-if="!isActiveUserEvaluator()"
            class="user-button"
            @click="onEvaluatorSignUpClick"
            :disabled="getVolunteerButtonIsDisabledAndTitle().disabled"
            :title="getVolunteerButtonIsDisabledAndTitle().title"
          >
            <div class="label-with-icon">
              <span class="label">Volunteer As Evaluator</span>
              <span class="icon"><EvaluatorIcon /></span>
            </div>
          </button>
          <button
            v-if="
              challengeData.challenge.state === ChallengeStateEnum.progress &&
              isActiveUserEvaluator()
            "
            class="user-button"
            @click="onStartEvaluatingClick"
          >
            <div class="label-with-icon">
              <span class="label">Start Evaluating</span>
            </div>
          </button>
        </div>
      </div>

      <!-- NOTE: possible expansion: choose round (implement multiple rounds) -->
      <div v-if="challengeData.challenge.state !== ChallengeStateEnum.open" class="glyph-table">
        <v-data-table-server
          :items="glyphsData || []"
          :items-length="10"
          :headers="[
            { title: '#', key: 'rank' },
            { title: 'Author', key: 'author' },
            { title: 'Glyph', key: 'glyph', sortable: false },
            { title: 'Flags', key: 'flags', sortable: false },
          ]"
          :items-per-page="glyphsItemsPerPage"
          :loading="glyphsLoading"
          @update:options="
            ({ page, itemsPerPage, sortBy }) => {
              glyphsCurrentPage = 1
              fetchPaginatedGlyphsData(page, itemsPerPage, getOrderByParam(sortBy[0]))
            }
          "
          sort-asc-icon="fa-solid fa-sort-up"
          sort-desc-icon="fa-solid fa-sort-down"
          sort-icon="fa-solid fa-sort"
          :fixed-header="true"
          height="min-content"
          :no-data-text="'No data available.'"
        >
          <template v-slot:item.rank="{ item }">
            {{ item.rank !== null ? item.rank : '-' }}
          </template>

          <template v-slot:item.author="{ item }">
            {{ item.author.username }}
          </template>

          <template v-slot:item.glyph="{ item }">
            <div class="glyph-image">
              <RouterLink :to="{ name: 'MGlyphDetail', params: { id: item.id } }">
                <MGlyphPreviewImage :file_id="item.file_id" />
              </RouterLink>
            </div>
          </template>

          <template v-slot:item.flags="{ item }">
            {{ item.flags.join(', ') }}
          </template>

          <template v-slot:bottom>
            <v-pagination
              :model-value="glyphsCurrentPage"
              @update:model-value="
                (newPage) => {
                  glyphsCurrentPage = newPage
                  fetchPaginatedGlyphsData(newPage, glyphsItemsPerPage)
                }
              "
              :length="glyphsTotalPages"
              :total-visible="5"
              next-icon="fa-solid fa-caret-right"
              prev-icon="fa-solid fa-caret-left"
            ></v-pagination>
          </template>
        </v-data-table-server>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import PopupNote from '@/components/PopupNote.vue'
import ChallengeState from '@/components/ChallengeState.vue'
import SolverIcon from '@/components/icons/SolverIcon.vue'
import EvaluatorIcon from '@/components/icons/EvaluatorIcon.vue'
import MGlyphPreviewImage from '@/components/MGlyphPreviewImage.vue'
import {
  ChallengeDetail,
  ChallengeGlyph,
  ChallengeUserSolverRelationshipType,
  ChallengeUserEvaluatorRelationshipType,
  ChallengeStateEnum,
} from '@/services/types'
import { mglyphClient } from '@/clients/mglyph_client'
import { authStore, popupStore } from '@/main'
import { useRouter } from 'vue-router'
import { ref } from 'vue'
const router = useRouter()

const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)
const glyphsLoading = ref<boolean>(true)
const glyphsCurrentPage = ref<number>(1)
const glyphsTotalPages = ref<number>(1)
const glyphsItemsPerPage = 10
const challengeData = ref<ChallengeDetail | null>(null)
const glyphsData = ref<ChallengeGlyph[] | null>(null)

type OrderByParam = 'rank_asc' | 'rank_desc' | 'creator_asc' | 'creator_desc'

function getOrderByParam(
  sortBy: { key: string; order: 'asc' | 'desc' } | null,
): OrderByParam | null {
  if (!sortBy) return null
  switch (sortBy.key) {
    case 'rank':
      return sortBy.order === 'asc' ? 'rank_asc' : 'rank_desc'
    case 'author':
      return sortBy.order === 'asc' ? 'creator_asc' : 'creator_desc'
    default:
      return null
  }
}

async function fetchChallengeData() {
  try {
    const response = await mglyphClient.get(`/challenges/${router.currentRoute.value.params.id}`, {
      authorizeEndpoint: authStore.user ? true : false,
    })
    challengeData.value = ChallengeDetail.fromAPIResponse(response.data)
  } catch (error) {
    console.error('Error fetching challenge data:', error)
    errorOccurred.value = true
  } finally {
    isLoading.value = false
  }
}

async function fetchPaginatedGlyphsData(
  page: number,
  itemsPerPage: number,
  orderBy: OrderByParam | null = null,
) {
  glyphsLoading.value = true
  try {
    const response = await mglyphClient.get(
      `/challenges/${router.currentRoute.value.params.id}/glyphs`,
      {
        authorizeEndpoint: false,
        params: {
          page: page,
          size: itemsPerPage,
          order_by: orderBy,
        },
      },
    )
    glyphsData.value = response.data.items.map((glyph: any) => {
      return ChallengeGlyph.fromAPIResponse(glyph)
    })
    glyphsTotalPages.value = response.data.total_pages
    glyphsCurrentPage.value = response.data.page
  } catch (error) {
    console.error('Error fetching glyphs data:', error)
    // TODO: Add popup error message
  } finally {
    glyphsLoading.value = false
  }
}

function isUserSolver(): boolean {
  return (
    (challengeData.value?.user_relationship?.user_solver_relationship &&
      challengeData.value?.user_relationship?.user_solver_relationship !==
        ChallengeUserSolverRelationshipType.none) ||
    false
  )
}

function isActiveUserEvaluator(): boolean {
  return (
    (challengeData.value?.user_relationship?.user_evaluator_relationship &&
      (challengeData.value.user_relationship.user_evaluator_relationship ===
        ChallengeUserEvaluatorRelationshipType.registered ||
        challengeData.value.user_relationship.user_evaluator_relationship ===
          ChallengeUserEvaluatorRelationshipType.evaluation_awaiting ||
        challengeData.value.user_relationship.user_evaluator_relationship ===
          ChallengeUserEvaluatorRelationshipType.evaluation_finished)) ||
    false
  )
}

function getVolunteerButtonIsDisabledAndTitle(): { disabled: boolean; title: string | undefined } {
  if (
    challengeData.value?.user_relationship?.user_evaluator_relationship ===
    ChallengeUserEvaluatorRelationshipType.pending_volunteer
  ) {
    return {
      disabled: true,
      title: 'Your request to become an evaluator is pending review by the administrators.',
    }
  } else if (
    challengeData.value?.user_relationship?.user_evaluator_relationship ===
    ChallengeUserEvaluatorRelationshipType.rejected_volunteer
  ) {
    return {
      disabled: true,
      title:
        'Your request to become an evaluator has been rejected by the administrators. You cannot volunteer as an evaluator for this challenge.',
    }
  } else if (
    challengeData.value?.user_relationship?.user_evaluator_relationship === undefined ||
    challengeData.value?.user_relationship?.user_evaluator_relationship ===
    ChallengeUserEvaluatorRelationshipType.none
  ) {
    return {
      disabled: false,
      title: undefined,
    }
  }
  return {
    disabled: true,
    title: undefined,
  }
}

async function reloadComponent() {
  isLoading.value = true
  errorOccurred.value = false
  glyphsLoading.value = true
  challengeData.value = null
  glyphsData.value = null
  await fetchChallengeData()
}

async function onEndSubmissionsClick() {
  try {
    const confirmed = confirm(
      'Are you sure you want to end submissions? This action cannot be undone, and users will no longer be able to submit their malleable glyphs.',
    )
    if (!confirmed) return

    await mglyphClient.post(
      `/challenges/${router.currentRoute.value.params.id}/end-submissions`,
      {},
      { authorizeEndpoint: true },
    )
    await reloadComponent()
  } catch (error: any) {
    console.error('Error ending submissions:', error)
    popupStore.addPopup(
      error.response?.data?.detail ||
        'An error occurred while ending submissions. Please try again later.',
      popupStore.PopupTypeEnum.error,
    )
  }
}

async function onEndChallengeClick() {
  try {
    const confirmed = confirm(
      'Are you sure you want to end the challenge? This action cannot be undone.',
    )
    if (!confirmed) return

    await mglyphClient.post(
      `/challenges/${router.currentRoute.value.params.id}/end-challenge`,
      {},
      { authorizeEndpoint: true },
    )
    await reloadComponent()
  } catch (error: any) {
    console.error('Error ending challenge:', error)
    popupStore.addPopup(
      error.response?.data?.detail ||
        'An error occurred while ending the challenge. Please try again later.',
      popupStore.PopupTypeEnum.error,
    )
  }
}

async function onParticipantSignUpClick() {
  try {
    await mglyphClient.post(
      `/challenges/${router.currentRoute.value.params.id}/register-solver`,
      {},
      { authorizeEndpoint: true },
    )
    await reloadComponent()
  } catch (error: any) {
    console.error('Error signing up as participant:', error)
    popupStore.addPopup(
      error.response?.data?.detail ||
        'An error occurred while signing up as a participant. Please try again later.',
      popupStore.PopupTypeEnum.error,
    )
  }
}

function onUploadGlyphClick() {
  console.log('Upload glyph clicked')
  // TODO:
  // router.push({ name: 'MGlyphUpload', params: { challengeId: router.currentRoute.value.params.id } })
}

async function onEvaluatorSignUpClick() {
  try {
    await mglyphClient.post(
      `/challenges/${router.currentRoute.value.params.id}/volunteer-evaluator`,
      {},
      { authorizeEndpoint: true },
    )
    await reloadComponent()
    // TODO: evaluator relationship zahrnout pending types
    console.log(challengeData.value)
  } catch (error: any) {
    console.error('Error signing up as evaluator:', error)
    popupStore.addPopup(
      error.response?.data?.detail ||
        'An error occurred while signing up as an evaluator. Please try again later.',
      popupStore.PopupTypeEnum.error,
    )
  }
}

function onStartEvaluatingClick() {
  console.log('Start evaluating clicked')
  // TODO:
  // router.push({ name: 'ChallengeEvaluation', params: { id: router.currentRoute.value.params.id } })
}

fetchChallengeData()
</script>

<style lang="css" scoped>
.title-and-state {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.state-and-user-info {
  display: flex;
  flex-direction: row-reverse;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;

  .user-info {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  i {
    font-size: 130%;
  }
}

.info-piece {
  margin: 6px 0;

  .label {
    font-weight: bold;
    margin-right: 4px;
  }
}

.buttons-container {
  margin: 22px 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 22px;

  .admin-button {
    background-color: rgb(var(--md-sys-color-tertiary, 0, 129, 167));
    color: rgb(var(--md-sys-color-on-tertiary, 255, 255, 255));
    border: none;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;

    &:hover {
      background-color: color-mix(
        in srgb,
        rgb(var(--md-sys-color-tertiary, 0, 129, 167)),
        rgb(var(--md-sys-color-on-tertiary, 255, 255, 255)) 10%
      );
    }
  }

  .user-buttons-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: 8px 12px;
  }

  .user-button {
    background-color: rgb(var(--md-sys-color-secondary, 0, 175, 185));
    color: rgb(var(--md-sys-color-on-secondary, 255, 255, 255));
    border: none;
    padding: 8px 16px;
    border-radius: 500px;
    cursor: pointer;
    font-size: 1rem;

    &:hover {
      background-color: color-mix(
        in srgb,
        rgb(var(--md-sys-color-secondary, 0, 175, 185)),
        rgb(var(--md-sys-color-on-secondary, 255, 255, 255)) 10%
      );
    }

    &:disabled {
      cursor: not-allowed;
      -webkit-filter: grayscale(1);
      opacity: 0.5;
    }
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

.glyph-table {
  margin-top: 24px;

  .glyph-image {
    margin: 8px 0;
    height: 100px;
    width: 100px;
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
