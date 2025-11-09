<template>
  <div class="mis-reservas-container">
    <h1>Mis Reservas</h1>
    <p>Aquí puedes ver el historial de los tours que has reservado.</p>

    <div v-if="isLoading" class="loading-state">
      Cargando tus reservas...
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="reservas.length > 0" class="reservas-grid">
      <div v-for="reserva in reservas" :key="reserva.id" class="reserva-card">
        
        <div class="card-header">
          <h3>Reserva #{{ reserva.id }}</h3>
          <span :class="['status', reserva.estado.toLowerCase()]">
            {{ reserva.estado }}
          </span>
        </div>
        
        <div class="card-body">
          <p><strong>ID del Tour:</strong> {{ reserva.tour_id }}</p>
          <p><strong>Personas:</strong> {{ reserva.cantidad_personas }}</p>
          <p><strong>Costo Total:</strong> ${{ parseFloat(reserva.costo_total).toLocaleString('es-CO') }}</p>
          <p><strong>Fecha:</strong> {{ new Date(reserva.fecha_reserva).toLocaleDateString('es-CO') }}</p>
        </div>
      </div>
    </div>

    <div v-if="!isLoading && reservas.length === 0 && !error" class="empty-state">
      <p>Aún no tienes ninguna reserva. ¡Anímate a explorar!</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'MisReservas',
  
  // Usamos 'setup' (Composition API) para una lógica más limpia
  setup() {
    // Inicializa el store para obtener el token
    const authStore = useAuthStore();
    
    // Define el estado reactivo
    const reservas = ref([]);
    const isLoading = ref(true);
    const error = ref(null);

    // Función para cargar las reservas
    const cargarReservas = async () => {
      try {
        // 1. Obtiene las cabeceras de autenticación (el Bearer Token)
        const config = authStore.getAuthHeaders();
        if (!config.headers) {
          throw new Error('Usuario no autenticado.');
        }

        // 2. Llama a la ruta protegida /mis-reservas
        const response = await axios.get('http://127.0.0.1:5002/mis-reservas', config);
        
        // 3. Guarda los datos en el estado
        reservas.value = response.data;

      } catch (e) {
        console.error(e);
        error.value = 'Error al cargar tus reservas. Por favor, intenta iniciar sesión de nuevo.';
      } finally {
        // 4. Quita el mensaje de "Cargando..."
        isLoading.value = false;
      }
    };

    // 'onMounted' es un hook de Vue que se ejecuta
    // automáticamente cuando el componente se carga
    onMounted(cargarReservas);

    // Expone las variables al template
    return {
      reservas,
      isLoading,
      error
    };
  }
};
</script>

<style scoped>
.mis-reservas-container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: var(--text-color);
  text-align: center;
  margin-bottom: 10px;
  font-weight: 800;
}

.mis-reservas-container > p { /* Target el <p> directo */
  color: var(--text-light);
  text-align: center;
  margin-bottom: 2.5rem;
  font-size: 1.25rem;
}

/* --- SOLUCIÓN A "CARGA HORIZONTAL" --- */
.reservas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.reserva-card {
  background-color: var(--bg-white);
  border-radius: var(--border-radius-large);
  box-shadow: var(--shadow-medium);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}

.reserva-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-large);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ecf0f1;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
}

.card-header h3 {
  margin: 0;
  color: var(--text-color);
}

.status {
  padding: 5px 12px;
  border-radius: 99px;
  font-weight: 700;
  font-size: 0.85rem;
  color: #fff;
}
.status.confirmada { background-color: var(--secondary-color); }
.status.pendiente { background-color: var(--warning-color); }
.status.cancelada { background-color: var(--danger-color); }

.card-body {
  padding: 1.5rem;
}

.card-body p {
  text-align: left;
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: var(--text-light);
}
.card-body p strong {
  color: var(--text-color);
  font-weight: 600;
  min-width: 110px;
  display: inline-block;
}

.card-body p:last-child {
  margin-bottom: 0;
}
</style>