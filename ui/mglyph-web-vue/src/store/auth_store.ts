import { defineStore } from 'pinia'
import { mglyphClient } from '@/clients/mglyph_client'
import { jwtDecode, type JwtPayload } from 'jwt-decode'
import { ref } from 'vue'

class LoggedUser {
  id: number
  username: string
  email: string
  role: string
  creation_time: Date

  constructor(
    id: number,
    username: string,
    email: string,
    role: string = 'user',
    creation_time: Date,
  ) {
    this.id = id
    this.username = username
    this.email = email
    this.role = role
    this.creation_time = creation_time
  }

  public static fromUserInfo(userInfo: any) {
    return new LoggedUser(
      userInfo.id,
      userInfo.username,
      userInfo.email,
      userInfo.role || 'user',
      new Date(userInfo.creation_time),
    )
  }
}

const useAuthStore = defineStore('auth', () => {
  const user = ref<null | LoggedUser>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  function googleLogin(googleToken: string) {
    return mglyphClient
      .post('/auth/google/', { credential: googleToken }, { authorizeEndpoint: false })
      .then((res) => {
        accessToken.value = res.data.access_token
        refreshToken.value = res.data.refresh_token
        user.value = LoggedUser.fromUserInfo(res.data.user_info)
      })
  }

  function createGoogleAccount(googleToken: string, username: string) {
    return mglyphClient
      .post(
        '/auth/google/create-user/',
        {
          username: username,
          credential: { credential: googleToken },
        },
        { authorizeEndpoint: false },
      )
      .then((res) => {
        accessToken.value = res.data.access_token
        refreshToken.value = res.data.refresh_token
        user.value = LoggedUser.fromUserInfo(res.data.user_info)
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
    createGoogleAccount,
    doTokenRefresh,
    isTokenValid,
    logout,
  }
})

export { useAuthStore }
