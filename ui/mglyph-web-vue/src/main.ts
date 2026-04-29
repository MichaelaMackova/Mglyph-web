// import './assets/main.css'
import axios from 'axios'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Pinia
import { createPinia } from 'pinia'
import { useAuthStore } from './store/auth_store'
import { usePopupStore } from './store/popup_store'
import { useEvaluationStore } from './store/evaluation_store'

const pinia = createPinia()
app.use(pinia)

const authStore = useAuthStore()
await authStore.initializeStoreFromLocalStorage()

const evaluationStore = useEvaluationStore()
evaluationStore.initializeStoreFromLocalStorage()

const popupStore = usePopupStore()

// Vuetify
// import 'vuetify/styles'
import { createVuetify } from 'vuetify'
// import * as components from 'vuetify/components'
// import * as directives from 'vuetify/directives'
import { VPagination } from 'vuetify/components/VPagination'
import {
  VDataTableServer,
  VSkeletonLoader,
  VTabs,
  VTab,
  VTabsWindow,
  VTabsWindowItem,
  VSlider,
  VForm,
  VTextField,
  VTextarea,
  VAutocomplete,
  VSwitch,
  VFileInput,
} from 'vuetify/components'

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
  colors: false as any, // NOTE: Type assertion to any to bypass type checking, empty object still sets some colors
}

const vuetify = createVuetify({
  // components,
  // directives,
  components: {
    VPagination,
    VDataTableServer,
    VSkeletonLoader,
    VTabs,
    VTab,
    VTabsWindow,
    VTabsWindowItem,
    VSlider,
    VForm,
    VTextField,
    VTextarea,
    VAutocomplete,
    VSwitch,
    VFileInput,
  },
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
} as any) // NOTE: Type assertion to any to bypass type checking for the options object, options type is not complete (scopes is missing) and causes type errors

app.use(router)
app.mount('#app')

export { authStore, popupStore, evaluationStore }
