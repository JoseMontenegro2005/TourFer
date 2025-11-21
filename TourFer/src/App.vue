<template>
  <div class="app-container">
    <!-- BARRA DE NAVEGACIÓN -->
    <nav class="navbar">
      <div class="nav-brand">
        <router-link to="/" class="logo">
          Tour<span class="highlight">Fer</span>
        </router-link>
      </div>

      <!-- Menú de navegación -->
      <div class="nav-menu">
        
        <!-- Saludo al usuario (Solo si está logueado) -->
        <div v-if="authStore.isAuthenticated" class="user-greeting">
          👋 Hola, <strong>{{ firstName }}</strong>
        </div>

        <router-link to="/" class="nav-link">Ver Tours</router-link>
        
        <template v-if="authStore.isAuthenticated">
          <router-link to="/mis-reservas" class="nav-link">Mis Reservas</router-link>
          
          <button @click="handleLogout" class="btn-logout">
            <span class="text">Cerrar Sesión</span>
            <span class="icon">🚪</span> <!-- Icono para móvil -->
          </button>
        </template>

        <template v-else>
          <router-link to="/login" class="btn-login">Iniciar Sesión</router-link>
        </template>
      </div>
    </nav>

    <!-- CONTENIDO DE LAS VISTAS -->
    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <p>© 2025 TourFer Colombia - Todos los derechos reservados.</p>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();
const router = useRouter();

// Obtener solo el primer nombre para que no ocupe tanto espacio
const firstName = computed(() => {
  if (authStore.userName) {
    return authStore.userName.split(' ')[0];
  }
  return 'Viajero';
});

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
/* ESTILOS GENERALES */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* NAVBAR */
.navbar {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
}

.highlight {
  color: #42b983;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: #2c3e50;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-link:hover, .nav-link.router-link-active {
  color: #42b983;
}

.user-greeting {
  background-color: #f0f9f4;
  color: #2c3e50;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  border: 1px solid #c3e6cb;
}

/* BOTONES */
.btn-login, .btn-logout {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s;
  border: none;
  display: inline-flex;
  align-items: center;
}

.btn-login {
  background-color: #42b983;
  color: white;
}

.btn-logout {
  background-color: transparent;
  color: #e74c3c;
  border: 1px solid #e74c3c;
}

.btn-logout:hover {
  background-color: #e74c3c;
  color: white;
}

.btn-logout .icon {
  display: none; /* Ocultar icono en escritorio */
}

/* MAIN Y FOOTER */
.main-content {
  flex: 1;
  background-color: #f8f9fa;
}

.footer {
  text-align: center;
  padding: 1.5rem;
  background-color: #2c3e50;
  color: white;
  font-size: 0.9rem;
}

/* ========================================== */
/* DISEÑO RESPONSIVE (MÓVIL)                  */
/* ========================================== */
@media (max-width: 768px) {
  .navbar {
    padding: 0.8rem 1rem;
    flex-direction: column; /* Apilar elementos */
    gap: 1rem;
  }

  .nav-menu {
    width: 100%;
    justify-content: space-between; /* Distribuir a lo ancho */
    gap: 0.5rem;
    flex-wrap: wrap; /* Permitir que bajen si no caben */
  }

  .nav-brand {
    width: 100%;
    text-align: center;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.5rem;
  }

  .user-greeting {
    order: -1; /* Poner el saludo arriba del todo en el menú */
    width: 100%;
    text-align: center;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
  }

  /* Enlaces más grandes para el dedo */
  .nav-link {
    padding: 0.5rem;
    font-size: 0.95rem;
  }

  /* Botón Logout compacto en móvil */
  .btn-logout {
    padding: 0.4rem 0.8rem;
    border: none; /* Quitar borde para ahorrar espacio */
  }
  
  .btn-logout .text {
    display: none; /* Ocultar texto "Cerrar Sesión" */
  }
  
  .btn-logout .icon {
    display: inline; /* Mostrar solo el icono de puerta */
    font-size: 1.2rem;
  }
}
</style>