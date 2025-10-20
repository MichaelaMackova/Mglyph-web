// import './assets/main.css'
import axios from 'axios'
import vue3GoogleLogin from 'vue3-google-login'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import { from } from 'env-var'

const env = from({
  BASE_URL: import.meta.env.BASE_URL,
  API_URL: import.meta.env.VITE_API_URL,
  GOOGLE_CLIENT_ID: import.meta.env.VITE_GOOGLE_CLIENT_ID,
})

const app = createApp(App)

// Allow CORS
axios.defaults.withCredentials = true
axios.defaults.baseURL = env.get('API_URL').required(true).asUrlString() // the FastAPI backend

// Google Auth
app.use(vue3GoogleLogin, {
  clientId: env.get('GOOGLE_CLIENT_ID').required(true).asString(),
})

app.use(router)
app.mount('#app')
