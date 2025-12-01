import { defineStore } from 'pinia'
import { mglyphClient } from '@/clients/mglyph_client'
import { jwtDecode, type JwtPayload } from 'jwt-decode'
import { ref } from 'vue'

const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  function googleLogin(googleToken: string) {
    return mglyphClient
      .post('/auth/google/', { credential: googleToken }, { authorizeEndpoint: false })
      .then((res) => {
        // console.log('Successfully logged in', res.data)
        accessToken.value = res.data.access_token
        refreshToken.value = res.data.refresh_token
      })
      .catch((err) => {
        console.error('Error logging in', err)
      })
  }

  async function doTokenRefresh() {
    if (!refreshToken.value) {
      return Promise.reject('No refresh token available')
    }

    await isTokenValid(false, false).then((isValid) => {
      if (!isValid) {
        logout()
        return Promise.reject('Refresh token is invalid or expired')
      }
    })

    return mglyphClient
      .get('/auth/refresh/', {
        authorizeEndpoint: false,
        headers: { Authorization: `Bearer ${refreshToken.value}` },
      })
      .then((res) => {
        accessToken.value = res.data.access_token
        refreshToken.value = res.data.refresh_token
      })
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
  }

  async function isTokenValid(
    isAccessToken: boolean = true,
    refresh: boolean = true,
  ): Promise<boolean> {
    const token = isAccessToken ? accessToken.value : refreshToken.value
    if (!token) return false
    try {
      const tokenPayload = jwtDecode<JwtPayload>(token)
      if (tokenPayload.exp) {
        var isValid = tokenPayload.exp * 1000 > Date.now()
        if (!isValid && refresh && isAccessToken) {
          // Try to refresh the token if it's expired
          await doTokenRefresh()
            .then(() => {
              isValid = true
            })
            .catch(() => {
              isValid = false
            })
        }
        return isValid
      }
      return false
    } catch (e) {
      return false
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    googleLogin,
    doTokenRefresh,
    isTokenValid,
    logout,
  }
})

// {
//   state: () => ({
//     user: null,
//     refreshTokenTimeout: null,
//   }),
//   actions: {
//     async login(username, password) {
//       this.user = await fetchWrapper.post(
//         `${baseUrl}/authenticate`,
//         { username, password },
//         { credentials: 'include' },
//       )
//       this.startRefreshTokenTimer()
//     },
//     logout() {
//       fetchWrapper.post(`${baseUrl}/revoke-token`, {}, { credentials: 'include' })
//       this.stopRefreshTokenTimer()
//       this.user = null
//       router.push('/login')
//     },
//     async refreshToken() {
//       this.user = await fetchWrapper.post(
//         `${baseUrl}/refresh-token`,
//         {},
//         { credentials: 'include' },
//       )
//       this.startRefreshTokenTimer()
//     },
//     startRefreshTokenTimer() {
//       // parse json object from base64 encoded jwt token
//       const jwtBase64 = this.user.jwtToken.split('.')[1]
//       const jwtToken = JSON.parse(atob(jwtBase64))

//       // set a timeout to refresh the token a minute before it expires
//       const expires = new Date(jwtToken.exp * 1000)
//       const timeout = expires.getTime() - Date.now() - 60 * 1000
//       this.refreshTokenTimeout = setTimeout(this.refreshToken, timeout)
//     },
//     stopRefreshTokenTimer() {
//       clearTimeout(this.refreshTokenTimeout)
//     },
//   },
// })

export { useAuthStore }
