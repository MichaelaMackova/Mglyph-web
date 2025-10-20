<template>
  <h1>Clicker</h1>
  <div v-if="!isUserLoggedIn">
    <GoogleLogin :callback="googleLoginCallback" />
    <!-- OR with popup -->
    <!-- <GoogleLogin :callback="googleLoginCallback" prompt /> -->
    <!-- OR with auto-login -->
    <!-- <GoogleLogin :callback="googleLoginCallback" prompt auto-login/> -->
  </div>
  <div v-else>
    <p>Welcome back!</p>
    <button @click="googleLogout">Logout</button>
    <div v-if="isLoading">Loading data...</div>
    <div v-else-if="errorOccurred">Error loading data.</div>
    <div v-else>
      <p>You've clicked {{ responseData.count }} times.</p>
      <button @click="addClick">+</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { ref } from 'vue'
import type { CallbackTypes } from 'vue3-google-login'

const isUserLoggedIn = ref<boolean>(false)
const accessToken = ref<string | null>(null)
const refreshToken = ref<string | null>(null)

// Google Sign-In
const googleLoginCallback: CallbackTypes.CredentialCallback = (response) => {
  // This callback will be triggered when the user selects or login to
  // his Google account from the popup
  // console.log('Handle the response', response)
  axios
    .post('/auth/google', {
      credential: response.credential,
    })
    .then((res) => {
      // console.log('Successfully logged in', res.data)
      isUserLoggedIn.value = true
      accessToken.value = res.data.access_token
      refreshToken.value = res.data.refresh_token
      fetchInitialCount()
    })
    .catch((err) => {
      console.error('Error logging in', err)
    })
}

function googleLogout() {
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
  accessToken.value = null
  refreshToken.value = null
  responseData.value = null
}

const responseData = ref<any>(null)
const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)

function addClick() {
  errorOccurred.value = false
  axios
    .get('/count/add-one/', {
      headers: {
        Authorization: `Bearer ${accessToken.value}`,
      },
    })
    .then((response) => {
      responseData.value = response.data
      errorOccurred.value = false
    })
    .catch((err) => {
      console.error(err)
      errorOccurred.value = true
    })
}

async function fetchInitialCount() {
  isLoading.value = true
  errorOccurred.value = false
  try {
    const response = await axios.get('/count', {
      headers: {
        Authorization: `Bearer ${accessToken.value}`,
      },
    })
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
