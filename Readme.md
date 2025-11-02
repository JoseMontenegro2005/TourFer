# Proyecto TourFer - Servicios Web

Este documento contiene las instrucciones para la configuración y ejecución del proyecto de dos APIs comunicadas.

### **Integrantes:**
* Manuel Felipe Fernandez
* José Luis Montenegro

---
### **Paso 1: Prerrequisitos**

Asegúrese de tener instalado el siguiente software:
1.  Python 3.x
2.  Un servidor de MySQL (como XAMPP, WAMP o MySQL Community Server)
3.  Postman (para realizar las pruebas)

---
### **Paso 2: Configuración de la Base de Datos**

Este es el paso más importante y debe realizarse primero.

1.  Abra su gestor de base de datos (MySQL Workbench, phpMyAdmin, etc.).
2.  Ejecute el contenido del archivo **`setup_database.sql`** que se encuentra en la raíz del proyecto. Este script creará los dos usuarios y las dos bases de datos necesarias.
3.  A continuación, ejecute el script **`catalogo_api/seed.sql`**. Esto creará las tablas y los datos de ejemplo para la API de Catálogo.
4.  Finalmente, ejecute el script **`reservas_api/seed.sql`**. Esto creará las tablas y los datos para la API de Reservas.

Al final de este paso, tendrá las dos bases de datos (`catalogo_db` y `reservas_db`) listas para ser usadas.

---
### **Paso 3: Ejecución de las APIs**

Ambas APIs deben ejecutarse simultáneamente en dos terminales separadas.

**Terminal 1 - `catalogo_api`:**
```bash
# 1. Navegar a la carpeta
cd catalogo_api

# 2. Activar entorno virtual
# Windows: 
venv\Scripts\activate
# macOS/Linux: 
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar el servidor (en el puerto 5001)
python app.py
```

**Terminal 2 - `reservas_api`:**
```bash
# 1. Navegar a la carpeta
cd reservas_api

# 2. Activar entorno virtual
# Windows: 
venv\Scripts\activate
# macOS/Linux: 
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar el servidor (en el puerto 5002)
python app.py
```

---
### **Paso 4: Pruebas**

1.  Con ambas APIs corriendo, puede proceder a realizar las pruebas.
2.  Se recomienda importar la colección de Postman (`TourFer.postman_collection.json`) y el entorno (`TourFer.postman_environment.json`) que se adjuntan en la entrega para facilitar las pruebas. 