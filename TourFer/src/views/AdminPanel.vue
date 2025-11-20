<template>
  <div class="admin-panel">
    <header class="admin-header">
      <h1>Panel de Administración</h1>
      <p>Gestiona el contenido de la plataforma TourFer.</p>
    </header>

    <div class="form-container manager-section">
      <h2>{{ editMode ? 'Editar Tour' : 'Crear Nuevo Tour' }}</h2>
      
      <form @submit.prevent="handleSubmitTour" class="form-grid">
        <div class="form-group span-2">
          <label for="tour-nombre">Nombre del Tour</label>
          <input id="tour-nombre" v-model="tourForm.nombre" type="text" required>
        </div>
        <div class="form-group span-2">
          <label for="tour-destino">Destino</label>
          <input id="tour-destino" v-model="tourForm.destino" type="text" required>
        </div>
        <div class="form-group span-4">
          <label for="tour-desc">Descripción</label>
          <textarea id="tour-desc" v-model="tourForm.descripcion" rows="3"></textarea>
        </div>
        <div class="form-group">
          <label for="tour-precio">Precio</label>
          <input id="tour-precio" v-model.number="tourForm.precio" type="number" step="1000" min="0" required>
        </div>
        <div class="form-group">
          <label for="tour-cupos">Cupos</label>
          <input id="tour-cupos" v-model.number="tourForm.cupos_disponibles" type="number" min="0" required>
        </div>
        <div class="form-group">
          <label for="tour-duracion">Duración (hrs)</label>
          <input id="tour-duracion" v-model.number="tourForm.duracion_horas" type="number" step="0.5" min="0" required>
        </div>
        <div class="form-group">
          <label for="tour-guia">ID Guía</label>
          <input id="tour-guia" v-model.number="tourForm.guia_id" type="number" min="1">
        </div>
        <div class="form-group span-4 form-actions">
          <button type="submit" class="btn btn-primary">
            {{ editMode ? 'Actualizar Tour' : 'Crear Tour' }}
          </button>
          <button v-if="editMode" @click="cancelEdit" type="button" class="btn" style="background-color: var(--text-muted); color: white;">
            Cancelar
          </button>
        </div>
      </form>
      <div v-if="formError" class="error-message">{{ formError }}</div>
    </div>

    <div class="manager-section">
      <h2>Lista de Tours</h2>
      <div v-if="isLoading" class="loading-state">Cargando tours...</div>
      <div v-if="loadError" class="error-message">{{ loadError }}</div>
      
      <div class="table-container">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Destino</th>
              <th>Precio</th>
              <th>Cupos</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tour in tours" :key="tour.id">
              <td>{{ tour.id }}</td>
              <td class="text-left">{{ tour.nombre }}</td>
              <td class="text-left">{{ tour.destino }}</td>
              <td>${{ tour.precio.toLocaleString('es-CO') }}</td>
              <td>{{ tour.cupos_disponibles }}</td>
              <td class="action-buttons">
                <button @click="startEdit(tour)" class="btn btn-small" style="background-color: var(--warning-color); color: white;">Editar</button>
                <button @click="handleDeleteTour(tour.id)" class="btn btn-small btn-danger">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!isLoading && tours.length === 0" class="empty-state">
        No se encontraron tours. ¡Crea uno nuevo!
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

const API_URL = 'https://tourfer-reservas.onrender.com';

const emptyForm = () => ({
  nombre: '',
  destino: '',
  descripcion: '',
  precio: 0,
  cupos_disponibles: 10,
  duracion_horas: 1,
  guia_id: 1,
  imagen_url: '' 
});

export default {
  name: 'AdminPanel',
  data() {
    return {
      tours: [],
      isLoading: true,
      loadError: null,
      formError: null,
      authStore: useAuthStore(),
      editMode: false,
      editTourId: null,
      tourForm: emptyForm(),
    };
  },
  
  methods: {
    async fetchTours() {
      this.isLoading = true;
      this.loadError = null;
      try {
        const response = await axios.get(`${API_URL}/public/tours`);
        this.tours = response.data;
      } catch (e) {
        console.error(e);
        this.loadError = 'Error al cargar la lista de tours.';
      } finally {
        this.isLoading = false;
      }
    },

    async handleSubmitTour() {
      this.formError = null;
      if (!this.authStore.isAdmin) {
        this.formError = 'No tienes permisos de administrador.';
        return;
      }
      
      try {
        const config = this.authStore.getAuthHeaders();
        
        if (this.editMode) {
          const url = `${API_URL}/admin/tours/${this.editTourId}`;
          await axios.put(url, this.tourForm, config);
        } else {
          const url = `${API_URL}/admin/tours`;
          await axios.post(url, this.tourForm, config);
        }
        
        this.resetForm();
        await this.fetchTours(); 
        
      } catch (e) {
        console.error(e);
        this.formError = 'Error al guardar el tour. Revisa los datos.';
      }
    },

    startEdit(tour) {
      this.editMode = true;
      this.editTourId = tour.id;
      this.tourForm = { ...tour };
      window.scrollTo(0, 0); 
    },

    resetForm() {
      this.editMode = false;
      this.editTourId = null;
      this.tourForm = emptyForm();
      this.formError = null;
    },
    
    cancelEdit() {
      this.resetForm();
    },
    
    async handleDeleteTour(id) {
      if (!confirm(`¿Estás seguro de que quieres eliminar el tour ID ${id}?`)) {
        return;
      }
      
      try {
        const config = this.authStore.getAuthHeaders();
        const url = `${API_URL}/admin/tours/${id}`;
        await axios.delete(url, config);
        await this.fetchTours(); 
      } catch (e) {
        console.error(e);
        alert('Error al eliminar el tour.');
      }
    }
  },
  
  mounted() {
    this.fetchTours();
  }
};
</script>

<style scoped>
.admin-panel {
  max-width: 1200px;
  margin: 0 auto;
}

.admin-header {
  text-align: center;
  margin-bottom: 2.5rem;
}
.admin-header h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}
.admin-header p {
  font-size: 1.25rem;
  color: var(--text-light);
  margin-top: 0;
}

.manager-section {
  background-color: var(--bg-white);
  padding: 2rem;
  border-radius: var(--border-radius-large);
  box-shadow: var(--shadow-medium);
  margin-bottom: 2rem;
}

.manager-section h2 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-color);
  margin-top: 0;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid var(--primary-color);
  padding-bottom: 10px;
  display: inline-block;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}
.span-2 { grid-column: span 2; }
.span-4 { grid-column: span 4; }

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  border-top: 1px solid var(--border-color);
  padding-top: 1.5rem;
  margin-top: 1rem;
}

.table-container {
  width: 100%;
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
  font-size: 0.95rem;
}

.admin-table th, .admin-table td {
  padding: 12px 15px;
  border-bottom: 1px solid var(--border-color);
  white-space: nowrap; 
  color: var(--text-color); 
}

.admin-table th {
  background-color: #ecf0f1;
  font-weight: 700;
  color: var(--text-color); 
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.admin-table tbody tr:nth-child(even) {
  background-color: var(--bg-main);
}
.admin-table tbody tr:hover {
  background-color: #e8f4fb;
}

.admin-table .text-left {
  text-align: left;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.btn-small {
  padding: 6px 10px;
  font-size: 0.85rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .span-2, .span-4 {
    grid-column: span 1;
  }
  .form-actions {
    flex-direction: column;
  }
  .btn {
    width: 100%;
  }
}
</style>
