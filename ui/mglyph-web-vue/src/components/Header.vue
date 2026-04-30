<template>
  <div class="header-container">
    <header>
      <div class="title">
        <RouterLink :to="{ name: 'Home' }">The Malleable Glyph Challenge</RouterLink>
      </div>

      <ul class="nav">
        <li><RouterLink :to="{ name: 'Home' }">Home</RouterLink></li>
        <li><RouterLink :to="{ name: 'About' }">About</RouterLink></li>
        <li><RouterLink :to="{ name: 'Challenges' }">Challenges</RouterLink></li>
        <!-- EXTENSION: <li><RouterLink :to="{ name: 'SelfEvaluation' }">Glyph Evaluation</RouterLink></li> -->
      </ul>

      <div class="login-container">
        <div class="login" ref="loginIconRef">
          <i
            v-show="authStore.user && !authStore.user.picture_url"
            class="fa-solid fa-circle-user fa-4x"
          ></i>
          <i v-show="!authStore.user" class="fa-regular fa-circle-user fa-4x"></i>
          <img
            v-if="authStore.user && authStore.user.picture_url"
            :src="authStore.user.picture_url"
            alt="Profile Picture"
          />
        </div>
      </div>
    </header>

    <div id="login-menu" ref="loginMenuRef" class="tooltip-top" v-show="loginMenuVisible">
      <!-- Logged out -->
      <ul v-show="!authStore.user">
        <li ref="loginButtonRef" @click="closeLoginMenu">Log in</li>
        <hr />
        <li @click="toggleTheme">
          <span v-show="currentTheme === 'light'"><i class="fa-solid fa-moon"></i> Dark</span>
          <span v-show="currentTheme === 'dark'"><i class="fa-solid fa-sun"></i> Light</span>
          Theme
        </li>
      </ul>
      <!-- Logged in -->
      <ul v-show="authStore.user">
        <li>My profile</li>
        <li>
          <RouterLink :to="{ name: 'MyChallenges' }"
            ><span ref="myChallengesLinkRef">My challenges</span></RouterLink
          >
        </li>
        <li>
          <RouterLink :to="{ name: 'MyInvites' }"
            ><span ref="myInvitesLinkRef">My invites</span></RouterLink
          >
        </li>
        <li>My glyphs</li>
        <hr v-if="authStore.user?.role === 'admin'" />
        <li v-if="authStore.user?.role === 'admin'">
          <RouterLink :to="{ name: 'AdminInvites' }"
            ><span ref="adminInvitesLinkRef">Admin invites</span></RouterLink
          >
        </li>
        <li v-if="authStore.user?.role === 'admin'">
          <RouterLink :to="{ name: 'AdminPrivileges' }"
            ><span ref="adminPrivilegesLinkRef">Admin privileges</span></RouterLink
          >
        </li>
        <hr />
        <li @click="toggleTheme">
          <span v-show="currentTheme === 'light'"><i class="fa-solid fa-moon"></i> Dark</span>
          <span v-show="currentTheme === 'dark'"><i class="fa-solid fa-sun"></i> Light</span>
          Theme
        </li>
        <hr />
        <li ref="logoutButtonRef" @click="logout">Log out</li>
      </ul>
    </div>
  </div>

  <div id="login-prompt-container" v-if="loginPromptVisible">
    <div id="login-prompt" ref="loginPromptRef">
      <h2 v-if="!loginLoading">Please Login</h2>
      <GoogleLogin v-if="!loginLoading" :callback="googleLoginCallback" prompt />
      <i class="fa-solid fa-spinner fa-spin-pulse fa-5x" v-if="loginLoading"></i>
    </div>
  </div>

  <div id="login-create-user-container" v-if="loginCreateUserVisible">
    <div id="login-create-user-prompt" ref="loginCreateUserPromptRef">
      <h2>Create Account</h2>
      <p>
        It seems like you don't have an account yet. Please enter a username to create your account.
      </p>
      <input v-model="username" type="text" placeholder="Username" />
      <button @click="createGoogleAccount">Create Account</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount, useTemplateRef } from 'vue'

/* ==================== THEME CHANGER ==================== */
import { onMounted } from 'vue'
const currentTheme = ref<string>('light')

function toggleTheme() {
  const htmlElement = document.documentElement
  htmlElement.classList.toggle('dark-theme')
  // Save preference to localStorage
  if (htmlElement.classList.contains('dark-theme')) {
    localStorage.setItem('theme-preference', 'dark')
    currentTheme.value = 'dark'
  } else {
    localStorage.setItem('theme-preference', 'light')
    currentTheme.value = 'light'
  }
}

function fetchTheme() {
  const htmlElement = document.documentElement
  const preferredTheme = localStorage.getItem('theme-preference')
  if (preferredTheme === 'dark') {
    htmlElement.classList.add('dark-theme')
    currentTheme.value = 'dark'
  } else if (preferredTheme === 'light') {
    htmlElement.classList.remove('dark-theme')
    currentTheme.value = 'light'
  } else {
    // If no preference is set, use system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      htmlElement.classList.add('dark-theme')
      currentTheme.value = 'dark'
    } else {
      htmlElement.classList.remove('dark-theme')
      currentTheme.value = 'light'
    }
  }
}

onMounted(() => {
  fetchTheme()
})
/* ==================== END - THEME CHANGER ==================== */

/* ==================== LOGIN MENU TOGGLE ==================== */
const loginMenuVisible = ref<boolean>(false)
const loginMenuEl = useTemplateRef('loginMenuRef')
const loginIconEl = useTemplateRef('loginIconRef')
const loginButtonEl = useTemplateRef('loginButtonRef')
const loginMenuOptionCloseEls = ref([
  loginButtonEl,
  useTemplateRef('myChallengesLinkRef'),
  useTemplateRef('logoutButtonRef'),
  useTemplateRef('myInvitesLinkRef'),
  useTemplateRef('adminInvitesLinkRef'),
])

function closeLoginMenu() {
  loginMenuVisible.value = false
}

function toggleLoginMenu(event: PointerEvent) {
  if (
    loginMenuEl.value &&
    !loginMenuEl.value.contains(event.target as Node) &&
    loginMenuVisible.value
  ) {
    loginMenuVisible.value = false
    return
  } else if (loginIconEl.value?.contains(event.target as Node)) {
    loginMenuVisible.value = true
    return
  }

  let close = false
  loginMenuOptionCloseEls.value.forEach((elementRef) => {
    if (elementRef.value?.contains(event.target as Node)) {
      close = true
    }
  })
  if (close) {
    loginMenuVisible.value = false
    return
  }
}
/* ==================== END - LOGIN MENU TOGGLE ==================== */

/* ==================== LOGIN PROMPT TOGGLE ==================== */
const loginPromptVisible = ref<boolean>(false)
const loginPromptEl = useTemplateRef('loginPromptRef')
const loginLoading = ref<boolean>(false)

function toggleLoginPrompt(event: PointerEvent) {
  if (
    !loginLoading.value &&
    loginPromptEl.value &&
    !loginPromptEl.value.contains(event.target as Node) &&
    loginPromptVisible.value
  ) {
    loginPromptVisible.value = false
  } else if (loginButtonEl.value?.contains(event.target as Node)) {
    loginPromptVisible.value = true
  }
}

function closeLoginPrompt() {
  loginPromptVisible.value = false
}
/* ==================== END - LOGIN PROMPT TOGGLE ==================== */

/* ==================== LOGIN AUTH ==================== */
import { authStore } from '@/main'
import type { CallbackTypes } from 'vue3-google-login'

let googleCredential: string | null = null
const createAccount = ref<boolean>(false)
const username = ref<string>('')

// Google Sign-In
const googleLoginCallback: CallbackTypes.CredentialCallback = (response) => {
  // This callback will be triggered when the user selects or login to
  // his Google account from the popup
  loginLoading.value = true
  authStore
    .googleLogin(response.credential)
    .then(() => {
      closeLoginPrompt()
      window.location.reload()
    })
    .catch((err) => {
      console.error('Error logging in', err)
    })
    .finally(() => {
      loginLoading.value = false
    })
}

function createGoogleAccount() {
  if (!username.value) {
    alert('Please enter a username')
    return
  }
  authStore
    .createGoogleAccount(googleCredential!, username.value)
    .then(() => {
      createAccount.value = false
      googleCredential = null
      closeCreateUserPrompt()
      closeLoginPrompt()
    })
    .catch((err) => {
      console.error('Error creating account and logging in', err)
    })
}

function logout() {
  // EXTENSION: Clear the session on the backend
  googleCredential = null
  authStore.logout()
  window.location.reload()
}
/* ==================== END - LOGIN AUTH ==================== */

/* ==================== CREATE USER TOGGLE ==================== */
// TODO: (NOT USED) delete anything related to creation of accounts
const loginCreateUserVisible = ref<boolean>(false)
const loginCreateUserEl = useTemplateRef('loginCreateUserPromptRef')

function toggleCreateUserPrompt(event: PointerEvent) {
  if (
    loginCreateUserEl.value &&
    !loginCreateUserEl.value.contains(event.target as Node) &&
    loginCreateUserVisible.value
  ) {
    loginCreateUserVisible.value = false
  }
}

function openCreateUserPrompt() {
  loginCreateUserVisible.value = true
}

function closeCreateUserPrompt() {
  loginCreateUserVisible.value = false
}
/* ==================== END - CREATE USER TOGGLE ==================== */

function eventListenerWrapper(event: PointerEvent) {
  if (loginCreateUserVisible.value) {
    toggleCreateUserPrompt(event)
  } else {
    toggleLoginPrompt(event)
    toggleLoginMenu(event)
  }
}

window.addEventListener<'click'>('click', eventListenerWrapper)

onBeforeUnmount(() => {
  window.removeEventListener<'click'>('click', eventListenerWrapper)
})
</script>

<style scoped lang="css">
.header-container {
  position: sticky;
  top: 0;
  z-index: 5;
}

header {
  width: 100%;
  height: 90px;
  padding: 0 20px;

  border-radius: 0 0 8px 8px;
  background: rgb(var(--md-sys-color-primary, 240, 113, 103));
  color: rgb(var(--md-sys-color-on-primary, 255, 255, 255));

  display: grid;
  grid-template-areas:
    'title login'
    'nav login';
  grid-template-columns: auto 120px;
  grid-template-rows: 55% 45%;
}

a,
a:visited,
a:link {
  color: inherit;
  text-decoration: none;
}

ul {
  list-style-type: none;
  margin: 0;
  padding: 0;

  display: flex;

  hr {
    border: none;
    border-top: 1px dashed
      color-mix(in srgb, rgb(var(--md-sys-color-outline, 103, 99, 94)) 50%, transparent);
    width: 92%;
    margin: 3px auto;
  }
}

.title {
  grid-area: title;
  display: flex;
  align-items: end;
  font-size: 36px;
  font-weight: bold;
}

ul.nav {
  grid-area: nav;
  overflow: hidden;

  li {
    padding: 5px 10px;
    align-content: center;
  }
}

.login-container {
  grid-area: login;
  align-items: center;
  display: flex;
  flex-direction: row-reverse;

  i {
    width: min-content;
    height: min-content;
  }

  img {
    width: 4em;
    object-fit: cover;
  }

  .login {
    height: 4em;
    width: 4em;
    border: 3px solid rgb(var(--md-sys-color-on-primary, 255, 255, 255));
    border-radius: 50%;
    overflow: hidden;

    & > * {
      /* centering */
      position: relative;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }
  }
}

#login-menu {
  position: absolute;
  top: 90px;
  right: 20px;
  background-color: rgb(var(--md-sys-color-surface-variant, 254, 241, 229));
  border-radius: 5px;
  box-shadow: -1.5px 3px 5px 0
    color-mix(in srgb, rgb(var(--md-sys-color-outline, 103, 99, 94)) 50%, transparent);
  color: rgb(var(--md-sys-color-on-surface-variant, 23, 21, 17));
  z-index: 5;

  ul {
    flex-direction: column;

    li {
      padding: 5px 10px;

      &:hover {
        cursor: pointer;
      }
    }
  }
}

.tooltip-top::after {
  content: '';
  position: absolute;
  border: 10px solid transparent;
  border-bottom-color: rgb(var(--md-sys-color-surface-variant, 254, 241, 229));
  bottom: 100%;
  right: 32px;
  transform: translateX(50%);
}

#login-prompt-container,
#login-create-user-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

#login-prompt,
#login-create-user-prompt {
  padding: 35px;
  max-width: 50%;

  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;

  background-color: rgb(var(--md-sys-color-surface, 255, 248, 244));
  border-radius: 4px;
  color: rgb(var(--md-sys-color-on-surface, 32, 27, 19));
}
</style>
