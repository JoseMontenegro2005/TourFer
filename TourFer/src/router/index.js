import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import ClienteTours from '@/views/ClienteTours.vue';
import LoginView from '@/views/LoginView.vue';
import AdminPanel from '@/views/AdminPanel.vue';
import RegisterView from '@/views/RegisterView.vue'; 
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
      path: '/register', 
      name: 'register',
      component: RegisterView,
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

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAdmin) {
    if (authStore.isAuthenticated && authStore.isAdmin) {
      next(); 
    } else {
      next('/'); 
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