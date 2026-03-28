import axios from 'axios'
import { env } from '@/services/env'
import { authStore } from '@/main'
import { ApiError, ApiResponseCode } from '@/services/errors'

declare module 'axios' {
  export interface AxiosRequestConfig {
    authorizeEndpoint?: boolean // Endpoints require authorization header
  }
}

const mglyphClient = axios.create({
  // Allow CORS
  withCredentials: true,
  baseURL: env.get('API_URL').required(true).asUrlString(),
  paramsSerializer: {
    indexes: null, // Prevent brackets in query strings for arrays
  },
  // headers: {
  //   'Content-Type': 'application/json',
  // }, TODO:
})

// Add a request interceptor to attach the JWT token to outgoing requests
mglyphClient.interceptors.request.use(
  async (config) => {
    if (config.authorizeEndpoint) {
      const isTokenValid = await authStore.isTokenValid(true, true)
      if (isTokenValid) {
        const token = authStore.accessToken // Get the token from Pinia store
        if (token) {
          config.headers = config.headers || {} // Ensure headers are defined
          config.headers['Authorization'] = `Bearer ${token}` // Add the Authorization header
        }
      } else {
        return Promise.reject(
          new ApiError(ApiResponseCode.TokenExpired, 'Access token is invalid or expired'),
        )
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Add a response interceptor to handle 401 errors and refresh the token
mglyphClient.interceptors.response.use(
  (response) => {
    return response // Return the response if it's successful
  },
  async (error) => {
    const originalRequest = error.config

    // Check for 401 status and ensure we haven't retried this request already
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      originalRequest.authorizeEndpoint
    ) {
      originalRequest._retry = true

      try {
        // Attempt to refresh the token
        await authStore.doTokenRefresh()

        const token = authStore.accessToken // Get the access token from Pinia store

        // Update the Authorization header and retry the original request
        originalRequest.headers['Authorization'] = `Bearer ${token}`
        return mglyphClient(originalRequest)
      } catch (err) {
        // Logout the user if token refresh fails
        authStore.logout()
        return Promise.reject(err)
      }
    }

    return Promise.reject(error)
  },
)

export { mglyphClient }
