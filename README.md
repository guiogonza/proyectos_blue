# 📊 Project Ops - Sistema de Gestión de Proyectos

Sistema completo de gestión de proyectos y asignaciones desarrollado con Streamlit y MySQL.

## 🚀 Características

- ✅ **Gestión de Personas**: CRUD completo con roles, tarifas y contactos
- ✅ **Gestión de Proyectos**: Creación, edición, cierre y eliminación con validaciones
- ✅ **Sprints**: Planificación y seguimiento de sprints por proyecto
- ✅ **Asignaciones**: Control de dedicación de personas a proyectos/sprints
- ✅ **Usuarios y Autenticación**: Sistema de login con roles (admin/viewer)
- ✅ **Dashboard**: Vista de portafolio y KPIs
- ✅ **Exportación**: Exportar datos a CSV
- ✅ **Bitácora**: Registro de eventos del sistema

## 📁 Estructura del Proyecto

```
project-ops/
├── apps/              # Módulos de UI (vistas Streamlit)
│   ├── dashboard/     # Dashboard principal
│   ├── personas/      # Gestión de personas
│   ├── proyectos/     # Gestión de proyectos
│   ├── sprints/       # Gestión de sprints
│   ├── asignaciones/  # Asignaciones persona-proyecto
│   └── usuarios/      # Administración de usuarios
├── domain/            # Lógica de negocio
│   ├── schemas/       # DTOs y validaciones
│   └── services/      # Servicios de negocio
├── infra/             # Infraestructura
│   ├── db/           # Conexión y migraciones
│   └── repositories/ # Acceso a datos
├── shared/            # Utilidades compartidas
│   ├── auth/         # Autenticación y autorización
│   └── utils/        # Utilidades varias
├── docker-compose.yml # Configuración Docker
└── requirements.txt   # Dependencias Python
```

## 🐳 Instalación con Docker

### Prerrequisitos
- Docker Desktop instalado y ejecutándose
- Git (opcional)

### Pasos

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd project-ops
```

2. **Iniciar los contenedores**
```bash
docker-compose up -d
```

3. **Verificar que los contenedores estén corriendo**
```bash
docker-compose ps
```

4. **Acceder a la aplicación**
- URL: http://localhost:8501
- Email: `admin@projectops.com`
- Contraseña: `admin123`

## 🗄️ Base de Datos

El proyecto incluye:
- **MySQL 8.0** en el puerto `3309`
- **Migraciones automáticas** al iniciar
- **Datos de demostración** incluidos en `project_ops_backup.sql`

### Conexión a la BD
```
Host: localhost
Puerto: 3309
Base de datos: project_ops
Usuario: project_ops_user
Contraseña: project_ops_pass
```

### Restaurar backup con datos
```bash
docker exec -i project_ops_mysql mysql -uproject_ops_user -pproject_ops_pass project_ops < project_ops_backup.sql
```

## 📦 Instalación Manual (sin Docker)

1. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno**
Crear archivo `.env` con:
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=project_ops
DB_USER=project_ops_user
DB_PASSWORD=project_ops_pass
APP_SECRET_KEY=your-secret-key
```

3. **Ejecutar migraciones SQL**
```bash
mysql -u root -p < infra/db/migrations/0001_init.sql
```

4. **Iniciar aplicación**
```bash
streamlit run apps/dashboard/main.py
```

## 🔧 Comandos Útiles

### Docker
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Detener servicios
docker-compose down

# Reiniciar aplicación
docker-compose restart app

# Acceder a MySQL
docker exec -it project_ops_mysql mysql -uproject_ops_user -pproject_ops_pass project_ops
```

### Backup y Restore
```bash
# Crear backup
docker exec project_ops_mysql mysqldump -uproject_ops_user -pproject_ops_pass project_ops > backup.sql

# Restaurar backup
docker exec -i project_ops_mysql mysql -uproject_ops_user -pproject_ops_pass project_ops < backup.sql
```

## 👥 Usuarios por Defecto

| Email | Contraseña | Rol |
|-------|-----------|-----|
| admin@projectops.com | admin123 | admin |
| admin@test.com | admin123 | admin |

## 🛠️ Tecnologías

- **Frontend**: Streamlit 1.51.0
- **Backend**: Python 3.11
- **Base de datos**: MySQL 8.0
- **ORM/Query**: PyMySQL
- **Validaciones**: Pydantic 2.x
- **Autenticación**: bcrypt
- **Contenedores**: Docker & Docker Compose

## 📊 Funcionalidades por Módulo

### Personas
- CRUD completo con validaciones
- Campos: nombre, rol, tarifa, cédula, contacto, email
- Activar/desactivar
- Validación de eliminación en cascada

### Proyectos
- Estados: Borrador, Activo, En pausa, Cerrado
- Asignación de PM
- Control de costos estimados y reales
- Eliminación en cascada de sprints y asignaciones

### Sprints
- Estados: Planificado, En curso, Cerrado
- Vinculación con proyectos
- Actividades y costos
- Eliminación de asignaciones asociadas

### Asignaciones
- Control de dedicación por porcentaje
- Validación de sobrecarga (>100%)
- Fechas de inicio y fin
- Vinculación opcional con sprints

## 🔒 Seguridad

- Contraseñas hasheadas con bcrypt
- Validación de sesiones
- Control de acceso por roles
- Validaciones de negocio en servicios

## 📝 Licencia

Este proyecto es privado y de uso interno.

## 👨‍💻 Contacto

Para soporte o consultas, contactar al administrador del sistema.
