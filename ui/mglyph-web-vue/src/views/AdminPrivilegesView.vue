<template>
  <div class="main-padding">
    <div v-if="authStore.user?.role !== 'admin'" class="main-top-margin">
      <PopupNote
        message="You do not have permission to access this page."
        type="error"
        :closable="false"
        width="max-content"
      />
    </div>
    <div v-else class="main-bottom-margin">
      <h1>Managing Admin Privileges</h1>

      <h2>Add new admin</h2>
      <div class="width-container">
        <v-autocomplete
          v-model="selectedItems"
          v-model:search="search"
          @update:search="onSearchInput"
          :items="fetchedUsers || []"
          :loading="loading"
          return-object
          label="Select New Admins"
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
        <button class="add-button" @click="onAdd" :disabled="isAdding">
          <div v-if="!isAdding" class="label-with-icon">
            <span class="label">Add Admin Privileges</span>
          </div>
          <div v-else class="label-with-icon">
            <span class="label">Sending invites...</span>
            <span class="icon"><i class="fa-solid fa-spinner fa-spin-pulse"></i></span>
          </div>
        </button>
      </div>

      <h2>Current Admins</h2>
      <div class="width-container">
        <v-data-table-server
          :items="adminUsersTable || []"
          :items-length="itemsPerTablePage"
          :headers="tableHeaders"
          :items-per-page="itemsPerTablePage"
          :loading="isTableLoading"
          :loading-text="'Loading admin users...'"
          :no-data-text="
            errorOccurredTable
              ? 'An error occurred while fetching admin users.'
              : 'No admin users available.'
          "
          sort-asc-icon="fa-solid fa-sort-up"
          sort-desc-icon="fa-solid fa-sort-down"
          sort-icon="fa-solid fa-sort"
          :fixed-header="true"
          height="min-content"
        >
          <template v-slot:item.username="{ item }">
            {{ item.username }}
          </template>

          <template v-slot:item.actions="{ item }">
            <button
              class="revoke-button"
              @click="onRevokeAdminPrivileges(item)"
              :disabled="totalTableItems <= 1"
            >
              Revoke Admin Privileges
            </button>
          </template>

          <template v-slot:bottom>
            <v-pagination
              :model-value="currentTablePage"
              @update:model-value="
                (page) => {
                  currentTablePage = page
                  fetchCurrentAdmins(page, itemsPerTablePage)
                }
              "
              :length="totalTablePages"
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

<script lang="ts" setup>
import PopupNote from '@/components/PopupNote.vue'
import { User, PaginatedData } from '@/services/types'
import { mglyphClient } from '@/clients/mglyph_client'
import { authStore, popupStore } from '@/main'
import { debounce } from '@/services/debounce'
import { ref } from 'vue'
import { type UUID } from 'crypto'

/* ========== Select and Add New Admins ========== */
const search = ref<string>('')
const selectedItems = ref<User[]>([])
const fetchedUsers = ref<User[] | null>(null)
const loading = ref<boolean>(false)
const isAdding = ref<boolean>(false)
const numberOfFetchedUsers = 10

async function fetchUsers(searchTerm: string) {
  loading.value = true
  try {
    const response = await mglyphClient.get('/users', {
      authorizeEndpoint: false,
      params: {
        username_contains: searchTerm !== '' ? searchTerm : null,
        is_admin: false, // only fetch non-admin users to add as new admins
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

async function onAdd() {
  if (selectedItems.value.length === 0) return

  isAdding.value = true
  for (const user of selectedItems.value) {
    try {
      await mglyphClient.patch(
        `/users/${user.id}/give-admin-role`,
        {},
        {
          authorizeEndpoint: true,
        },
      )
    } catch (err) {
      console.error('Failed add as admin:', err)
      popupStore.addPopup(
        "Failed to give 'admin' role to " + user.username,
        popupStore.PopupTypeEnum.error,
      )
    }
  }
  selectedItems.value = []
  fetchCurrentAdmins(currentTablePage.value, itemsPerTablePage)
  isAdding.value = false
}
/* ========== End of Select and Add New Admins ========== */

/* ========== Admin Table ========== */
const isTableLoading = ref<boolean>(false)
const errorOccurredTable = ref<boolean>(false)
const currentTablePage = ref<number>(1)
const itemsPerTablePage = 10
const totalTablePages = ref<number>(1)
const totalTableItems = ref<number>(0)
const adminUsersTable = ref<User[] | null>(null)
const tableHeaders = [
  { title: 'Username', key: 'username', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false },
]

async function fetchCurrentAdmins(page: number, size: number) {
  isTableLoading.value = true
  errorOccurredTable.value = false
  try {
    const response = await mglyphClient.get('/users', {
      authorizeEndpoint: false,
      params: {
        is_admin: true,
        size: size,
        page: page,
      },
    })
    const paginatedAdmins = PaginatedData.fromAPIResponse(
      response.data,
      (user: any) => new User(user.id, user.username),
    )
    adminUsersTable.value = paginatedAdmins.items
    totalTablePages.value = paginatedAdmins.total_pages
    currentTablePage.value = paginatedAdmins.current_page
    totalTableItems.value = paginatedAdmins.total_count
  } catch (err) {
    console.error('Failed to fetch current admins:', err)
    errorOccurredTable.value = true
    popupStore.addPopup(
      'Failed to load current admin users. Please try again later.',
      popupStore.PopupTypeEnum.error,
    )
  } finally {
    isTableLoading.value = false
  }
}

async function onRevokeAdminPrivileges(user: User) {
  try {
    await mglyphClient.patch(
      `/users/${user.id}/revoke-admin-role`,
      {},
      {
        authorizeEndpoint: true,
      },
    )
    popupStore.addPopup(
      `Successfully revoked admin privileges for ${user.username}.`,
      popupStore.PopupTypeEnum.info,
    )
    fetchCurrentAdmins(currentTablePage.value, itemsPerTablePage)
  } catch (err) {
    console.error('Failed to revoke admin privileges:', err)
    popupStore.addPopup(
      "Failed to revoke 'admin' role. Please try again later.",
      popupStore.PopupTypeEnum.error,
    )
  }
}
/* ========== End of Admin Table ========== */

if (authStore.user?.role === 'admin') {
  fetchCurrentAdmins(currentTablePage.value, itemsPerTablePage)
}
</script>

<style lang="css" scoped>
.width-container {
  max-width: 750px;
}

.add-button {
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

.revoke-button {
  padding: 5px 10px;
  border-radius: 6px;
  cursor: pointer;

  background-color: rgb(var(--md-sys-color-tertiary-container, 157, 213, 230));
  color: rgb(var(--md-sys-color-on-tertiary-container, 0, 39, 51));
  border: rgba(var(--md-sys-color-on-tertiary-container, 0, 39, 51), 0.2) 1px solid;

  &:hover:not(:disabled) {
    background-color: rgb(var(--md-sys-color-error-container, 230, 167, 167));
    color: rgb(var(--md-sys-color-on-error-container, 51, 7, 7));
  }

  &:disabled {
    cursor: not-allowed;
    -webkit-filter: grayscale(1);
    opacity: 0.7;
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
