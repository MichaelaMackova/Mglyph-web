<template>
  <div class="header-container">
    <header class="main-padding">
      <div class="title">
        <RouterLink :to="{ name: 'Home' }">The Malleable Glyph Challenge</RouterLink>
      </div>

      <ul class="nav">
        <li><RouterLink :to="{ name: 'Home' }">Home</RouterLink></li>
        <li><RouterLink :to="{ name: 'Clicker' }">Clicker</RouterLink></li>
        <li><RouterLink :to="{ name: 'Home' }">About</RouterLink></li>
        <li><RouterLink :to="{ name: 'Home' }">Challenges</RouterLink></li>
      </ul>

      <div class="login-container">
        <div class="login" ref="loginIconRef">
          <i v-show="authStore.user" class="fa-solid fa-circle-user fa-4x"></i>
          <i v-show="!authStore.user" class="fa-regular fa-circle-user fa-4x"></i>
        </div>
      </div>
    </header>

    <div id="login-menu" ref="loginMenuRef" class="tooltip-top" v-show="loginMenuVisible">
      <!-- Logged out -->
      <ul v-show="!authStore.user">
        <li ref="loginButtonRef" @click="closeLoginMenu">Log in</li>
        <li @click="toggleTheme">
          <span v-show="currentTheme === 'dark'"><i class="fa-solid fa-moon"></i> Dark</span>
          <span v-show="currentTheme === 'light'"><i class="fa-solid fa-sun"></i> Light</span>
          Theme
        </li>
      </ul>
      <!-- Logged in -->
      <ul v-show="authStore.user">
        <li @click="toggleTheme">
          <span v-show="currentTheme === 'dark'"><i class="fa-solid fa-moon"></i> Dark</span>
          <span v-show="currentTheme === 'light'"><i class="fa-solid fa-sun"></i> Light</span>
          Theme
        </li>
        <li @click="logout">Log out</li>
      </ul>
    </div>
  </div>

  <div id="login-prompt-container" v-if="loginPromptVisible">
    <div id="login-prompt" ref="loginPromptRef">
      <h2>Please Login</h2>
      <GoogleLogin :callback="googleLoginCallback" prompt />
    </div>
  </div>

  <div id="login-create-user-container" v-if="loginCreateUserVisible">
    <div id="login-create-user-prompt" ref="loginCreateUserPromptRef">
      <h2>Create Account</h2>
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
  } else if (loginIconEl.value?.contains(event.target as Node)) {
    loginMenuVisible.value = true
  }
}
/* ==================== END - LOGIN MENU TOGGLE ==================== */

/* ==================== LOGIN PROMPT TOGGLE ==================== */
const loginPromptVisible = ref<boolean>(false)
const loginPromptEl = useTemplateRef('loginPromptRef')
const loginButtonEl = useTemplateRef('loginButtonRef')

function toggleLoginPrompt(event: PointerEvent) {
  if (
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
  googleCredential = response.credential
  authStore
    .googleLogin(googleCredential)
    .then(() => {
      createAccount.value = false
      googleCredential = null
      closeLoginPrompt()
    })
    .catch((err) => {
      if (err.response?.data?.err_code === 404) {
        // TODO: Define this error code in the backend and frontend
        // If the error is because the account doesn't exist, show the create account form
        openCreateUserPrompt()
      } else {
        console.error('Error logging in', err)
      }
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
  // TODO: Clear the session on the backend
  googleCredential = null
  authStore.logout()
}
/* ==================== END - LOGIN AUTH ==================== */

/* ==================== CREATE USER TOGGLE ==================== */
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
}

header {
  width: 100%;
  height: 90px;

  border-radius: 0 0 8px 8px;
  background: var(--md-sys-color-primary, #f07167);
  color: var(--md-sys-color-on-primary, #ffffff);

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

  i,
  .login {
    height: min-content;
    width: min-content;
  }
}

#login-menu {
  position: absolute;
  top: 90px;
  right: 20px;
  background-color: var(--md-sys-color-surface-variant, #fef1e5);
  border-radius: 5px;
  box-shadow: -1.5px 3px 5px 0
    color-mix(in srgb, var(--md-sys-color-outline, #67635e) 50%, transparent);
  color: var(--md-sys-color-on-surface-variant, #171511);

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
  border-bottom-color: var(--md-sys-color-surface-variant, #fef1e5);
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
  z-index: 2;
}

#login-prompt,
#login-create-user-prompt {
  padding: 35px;

  display: flex;
  flex-direction: column;
  align-items: center;

  background-color: var(--md-sys-color-surface, #fff8f4);
  border-radius: 4px;
  color: var(--md-sys-color-on-surface, #201b13);
}
</style>
