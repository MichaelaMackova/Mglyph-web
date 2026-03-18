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
  picture_url: string | null

  constructor(
    id: number,
    username: string,
    email: string,
    role: string = 'user',
    creation_time: Date,
    picture_url: string | null = null,
  ) {
    this.id = id
    this.username = username
    this.email = email
    this.role = role
    this.creation_time = creation_time
    this.picture_url = picture_url
  }

  public static fromUserInfo(userInfo: any) {
    return new LoggedUser(
      userInfo.id,
      userInfo.username,
      userInfo.email,
      userInfo.role || 'user',
      new Date(userInfo.creation_time),
      userInfo.picture_url || null
    )
  }
}

const useAuthStore = defineStore('auth', () => {
  const user = ref<null | LoggedUser>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  function initializeStoreFromLocalStorage() {
    const storedAccessToken = localStorage.getItem('accessToken')
    const storedRefreshToken = localStorage.getItem('refreshToken')
    const storedUserInfo = localStorage.getItem('userInfo')

    if (storedAccessToken) {
      accessToken.value = storedAccessToken
    }
    if (storedRefreshToken) {
      refreshToken.value = storedRefreshToken
    }
    if (storedUserInfo) {
      try {
        user.value = LoggedUser.fromUserInfo(JSON.parse(storedUserInfo))
      } catch (e) {
        console.error('Error parsing userInfo from localStorage:', e)
        localStorage.removeItem('userInfo')
      }
    }
  }

  function saveStoreToLocalStorage() {
    if (accessToken.value) {
      localStorage.setItem('accessToken', accessToken.value)
    } else {
      localStorage.removeItem('accessToken')
    }

    if (refreshToken.value) {
      localStorage.setItem('refreshToken', refreshToken.value)
    } else {
      localStorage.removeItem('refreshToken')
    }

    if (user.value) {
      localStorage.setItem('userInfo', JSON.stringify(user.value))
    } else {
      localStorage.removeItem('userInfo')
    }
  }

  function googleLogin(googleToken: string) {
    return mglyphClient
      .post('/auth/google/', { credential: googleToken }, { authorizeEndpoint: false })
      .then((res) => {
        accessToken.value = res.data.access_token
        refreshToken.value = res.data.refresh_token
        user.value = LoggedUser.fromUserInfo(res.data.user_info)
        user.value.picture_url = res.data.picture_url || null
        saveStoreToLocalStorage()
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
        user.value.picture_url = res.data.picture_url || null
        saveStoreToLocalStorage()
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
    saveStoreToLocalStorage()
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
    initializeStoreFromLocalStorage,
  }
})

export { useAuthStore }
