import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import './index.css'
import './assets/main.css'
import './assets/themes.css'
import './assets/human-care-patient.css'
import { initTheme, setPortalTheme } from './composables/useTheme.js'

initTheme()

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
