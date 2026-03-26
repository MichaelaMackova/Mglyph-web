// import './assets/main.css'
import axios from 'axios'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// // Allow CORS TODO: odstranit
// axios.defaults.withCredentials = true
// axios.defaults.baseURL = env.get('API_URL').required(true).asUrlString() // the FastAPI backend

// Pinia
import { createPinia } from 'pinia'
import { useAuthStore } from './store/auth_store'
import { usePopupStore } from './store/popup_store'

const pinia = createPinia()
app.use(pinia)

const authStore = useAuthStore()
await authStore.initializeStoreFromLocalStorage()

const popupStore = usePopupStore()

// Vuetify
// import 'vuetify/styles'
import { createVuetify } from 'vuetify'
// import * as components from 'vuetify/components'
// import * as directives from 'vuetify/directives'
import { VPagination } from 'vuetify/components/VPagination'

const minimalTheme = {
  variables: {
    'border-opacity': 0.12,
    'high-emphasis-opacity': 0.87,
    'medium-emphasis-opacity': 0.6,
    'disabled-opacity': 0.38,
    'idle-opacity': 0.04,
    'hover-opacity': 0.04,
    'focus-opacity': 0.12,
    'selected-opacity': 0.08,
    'activated-opacity': 0.12,
    'pressed-opacity': 0.12,
    'dragged-opacity': 0.08,
    'theme-overlay-multiplier': 1.5,
  },
}

const vuetify = createVuetify({
  // components,
  // directives,
  components: { VPagination },
  theme: {
    defaultTheme: 'minimalTheme',
    themes: {
      minimalTheme,
    },
  },
})
app.use(vuetify)

// Google Auth
import vue3GoogleLogin from 'vue3-google-login'
import { env } from './services/env'
app.use(vue3GoogleLogin, {
  clientId: env.get('GOOGLE_CLIENT_ID').required(true).asString(),
  scopes:
    'email profile https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid',
})

app.use(router)
app.mount('#app')

export { authStore, popupStore }
