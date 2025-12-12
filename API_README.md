# API REST - Project Ops

API REST para gestión de proyectos, sprints, personas y asignaciones.

## 🚀 Inicio Rápido

### Levantar la API

```bash
docker-compose up api
```

La API estará disponible en: **http://localhost:8000**

Documentación interactiva: **http://localhost:8000/docs**

## 🔐 Autenticación

La API usa **HTTP Basic Authentication**. Debes enviar las credenciales en cada request.

**Credenciales de ejemplo:**
- Usuario: `admin@projectops.com`
- Password: `admin123`

### Ejemplo con curl:

```bash
curl -u admin@projectops.com:admin123 http://localhost:8000/api/personas
```

### Ejemplo con Python:

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    'http://localhost:8000/api/personas',
    auth=HTTPBasicAuth('admin@projectops.com', 'admin123')
)
print(response.json())
```

### Ejemplo con JavaScript (fetch):

```javascript
const username = 'admin@projectops.com';
const password = 'admin123';
const credentials = btoa(`${username}:${password}`);

fetch('http://localhost:8000/api/personas', {
    headers: {
        'Authorization': `Basic ${credentials}`
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📋 Endpoints Disponibles

### Personas
- `GET /api/personas` - Listar todas las personas
  - Query params: `search`, `activo`
- `GET /api/personas/{id}` - Obtener persona por ID

### Proyectos
- `GET /api/proyectos` - Listar todos los proyectos
  - Query params: `search`, `estado`
- `GET /api/proyectos/{id}` - Obtener proyecto por ID

### Sprints
- `GET /api/sprints` - Listar todos los sprints
  - Query params: `proyecto_id`, `estado`, `search`
- `GET /api/sprints/{id}` - Obtener sprint por ID

### Asignaciones
- `GET /api/asignaciones` - Listar todas las asignaciones
  - Query params: `persona_id`, `proyecto_id`, `solo_activas`
- `GET /api/asignaciones/{id}` - Obtener asignación por ID

### Usuarios
- `GET /api/usuarios` - Listar usuarios (solo admin)

### Health Check
- `GET /api/health` - Verificar estado de la API
- `GET /` - Información de la API

## 📖 Ejemplos de Uso

### Listar personas activas

```bash
curl -u admin@projectops.com:admin123 \
  "http://localhost:8000/api/personas?activo=true"
```

### Buscar proyectos por nombre

```bash
curl -u admin@projectops.com:admin123 \
  "http://localhost:8000/api/proyectos?search=Inventario"
```

### Obtener sprints de un proyecto específico

```bash
curl -u admin@projectops.com:admin123 \
  "http://localhost:8000/api/sprints?proyecto_id=1"
```

### Obtener asignaciones de una persona

```bash
curl -u admin@projectops.com:admin123 \
  "http://localhost:8000/api/asignaciones?persona_id=1&solo_activas=true"
```

## 🌐 Servidor Remoto

Para acceder a la API en el servidor remoto:

**URL:** http://164.68.118.86:8002

**Documentación:** http://164.68.118.86:8002/docs

```bash
curl -u admin@projectops.com:admin123 \
  http://164.68.118.86:8002/api/personas
```

## 📚 Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Desde la documentación puedes:
1. Ver todos los endpoints disponibles
2. Probar los endpoints directamente
3. Ver los schemas de request/response
4. Autenticarte con el botón "Authorize"

## 🔧 Formato de Respuesta

Todos los endpoints retornan JSON. Ejemplo:

```json
[
  {
    "id": 1,
    "nombre": "Juan Pérez",
    "rol": "Desarrollador Senior",
    "tarifa_interna": 80000.00,
    "cedula": "1234567890",
    "numero_contacto": "555-0101",
    "correo": "juan.perez@company.com",
    "activo": true
  }
]
```

## 🛠️ Desarrollo Local

Para ejecutar la API en modo desarrollo:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar API
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Docker

### Levantar solo la API

```bash
docker-compose up api
```

### Levantar API + Base de datos

```bash
docker-compose up mysql api
```

### Levantar todo (API + Dashboard + BD)

```bash
docker-compose up
```

## 📊 Códigos de Estado HTTP

- `200 OK` - Solicitud exitosa
- `401 Unauthorized` - Credenciales inválidas
- `403 Forbidden` - Sin permisos suficientes
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

## 🔒 CORS

La API tiene CORS habilitado para permitir requests desde cualquier origen. En producción, se recomienda configurar orígenes específicos.

## 📝 Notas

- Todos los endpoints requieren autenticación
- El endpoint `/api/usuarios` solo es accesible para usuarios con rol `admin`
- Los timestamps están en timezone `America/Bogota`
- Las fechas se retornan en formato ISO 8601: `YYYY-MM-DD`
