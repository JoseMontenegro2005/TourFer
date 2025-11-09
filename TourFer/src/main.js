import { createApp } from 'vue'
// 1. Importa Pinia
import { createPinia } from 'pinia'

import App from './App.vue'
// 2. Importa tu router (que ya tiene las rutas y el guardia)
import router from './router'

// Importa los estilos CSS por defecto
import './assets/main.css'

// Crea la aplicación
const app = createApp(App)

// 3. Dile a Vue que "use" Pinia (el cerebro)
app.use(createPinia())
// 4. Dile a Vue que "use" el Router (el mapa)
app.use(router)

// Monta la aplicación en el DOM
app.mount('#app')