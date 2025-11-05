import { from } from 'env-var'

export const env = from({
  BASE_URL: import.meta.env.BASE_URL,
  API_URL: import.meta.env.VITE_API_URL,
  GOOGLE_CLIENT_ID: import.meta.env.VITE_GOOGLE_CLIENT_ID,
})
