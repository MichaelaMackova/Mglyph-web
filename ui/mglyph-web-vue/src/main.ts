// import './assets/main.css'
import axios from 'axios'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// // Allow CORS TODO: odstranit
// axios.defaults.withCredentials = true
// axios.defaults.baseURL = env.get('API_URL').required(true).asUrlString() // the FastAPI backend

import { createPinia } from 'pinia'
import { useAuthStore } from './store/auth_store'

const pinia = createPinia()
app.use(pinia)

const authStore = useAuthStore()
authStore.initializeStoreFromLocalStorage()

// Google Auth
import vue3GoogleLogin from 'vue3-google-login'
import { env } from './services/env'
app.use(vue3GoogleLogin, {
  clientId: env.get('GOOGLE_CLIENT_ID').required(true).asString(),
  scopes: 'email profile https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid',
})

app.use(router)
app.mount('#app')

export { authStore }
