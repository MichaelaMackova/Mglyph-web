<template>
  <h1>Clicker</h1>
  <div v-if="!isUserLoggedIn">
    <!-- <GoogleLogin :callback="googleLoginCallback" /> -->
    <!-- OR with popup -->
    <!-- <GoogleLogin :callback="googleLoginCallback" prompt /> -->
    <!-- OR with auto-login -->
    <GoogleLogin :callback="googleLoginCallback" prompt auto-login />
  </div>
  <div v-else>
    <p>Welcome back!</p>
    <button @click="logout">Logout</button>
    <div v-if="isLoading">Loading data...</div>
    <div v-else-if="errorOccurred">Error loading data.</div>
    <div v-else>
      <p>You've clicked {{ responseData.count }} times.</p>
      <button @click="addClick">+</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { CallbackTypes } from 'vue3-google-login'
import { authStore } from '@/main'
import { mglyphClient } from '@/clients/mglyph_client'
import { ApiErrorCode } from '@/services/errors'

const isUserLoggedIn = ref<boolean>(false)

// Google Sign-In
const googleLoginCallback: CallbackTypes.CredentialCallback = (response) => {
  // This callback will be triggered when the user selects or login to
  // his Google account from the popup
  // console.log('Handle the response', response)

  authStore
    .googleLogin(response.credential)
    .then(() => {
      isUserLoggedIn.value = true
      fetchInitialCount()
    })
    .catch((err) => {
      console.error('Error logging in', err)
    })

  // axios
  //   .post('/auth/google', {
  //     credential: response.credential,
  //   })
  //   .then((res) => {
  //     // console.log('Successfully logged in', res.data)
  //     isUserLoggedIn.value = true
  //     accessToken.value = res.data.access_token
  //     refreshToken.value = res.data.refresh_token
  //     fetchInitialCount()
  //   })
  //   .catch((err) => {
  //     console.error('Error logging in', err)
  //   })
}

function logout() {
  // TODO: Clear the session on the backend
  // axios
  //   .post('/auth/logout')
  //   .then(() => {
  //     console.log('Successfully logged out')
  //     isUserLoggedIn.value = false
  //   })
  //   .catch((err) => {
  //     console.error('Error logging out', err)
  //   })
  isUserLoggedIn.value = false
  responseData.value = null
  authStore.logout()
}

const responseData = ref<any>(null)
const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)

function addClick() {
  errorOccurred.value = false
  mglyphClient
    .get('/count/add-one/', { authorizeEndpoint: true })
    .then((response) => {
      responseData.value = response.data
      errorOccurred.value = false
    })
    .catch((err) => {
      if (err.response?.status === 401 || err.code === ApiErrorCode.TokenExpired) {
        // Unauthorized, log out
        logout()
      } else {
        console.error(err)
        errorOccurred.value = true
      }
    })
}

async function fetchInitialCount() {
  isLoading.value = true
  errorOccurred.value = false
  try {
    const response = await mglyphClient.get('/count', { authorizeEndpoint: true })
    responseData.value = response.data
    errorOccurred.value = false
  } catch (err) {
    console.error(err)
    errorOccurred.value = true
  } finally {
    isLoading.value = false
  }
}
</script>
