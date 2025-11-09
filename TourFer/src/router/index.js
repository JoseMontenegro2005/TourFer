import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

// --- IMPORTACIÓN DE VISTAS ---
// Asegúrate de que todas tus vistas estén importadas aquí
import ClienteTours from '@/views/ClienteTours.vue';
import LoginView from '@/views/LoginView.vue';
import AdminPanel from '@/views/AdminPanel.vue';
import RegisterView from '@/views/RegisterView.vue'; // <-- ESTA LÍNEA ES LA CLAVE
// (Solo 'mis-reservas' queda pendiente)
import MisReservasView from '@/views/MisReservas.vue'; 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: ClienteTours,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register', // <-- RUTA DESCOMENTADA
      name: 'register',
      component: RegisterView, // <-- AHORA FUNCIONA PORQUE FUE IMPORTADO
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminPanel,
      meta: { requiresAdmin: true }, 
    },
    {
      path: '/mis-reservas',
      name: 'mis-reservas',
      component: MisReservasView,
      meta: { requiresAuth: true }, 
    },
  ],
});

// --- GUARDIA DE SEGURIDAD DEL ROUTER (Sin cambios) ---
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAdmin) {
    if (authStore.isAuthenticated && authStore.isAdmin) {
      next(); 
    } else {
      next('/login'); 
    }
  } 
  else if (to.meta.requiresAuth) {
    if (authStore.isAuthenticated) {
      next(); 
    } else {
      next('/login'); 
    }
  } 
  else {
    next(); 
  }
});

export default router;