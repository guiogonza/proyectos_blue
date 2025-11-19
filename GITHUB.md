# 🔗 Guía para Subir a GitHub

## Paso 1: Crear repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `project-ops`
3. Descripción: `Sistema de gestión de proyectos con Streamlit y MySQL`
4. **NO inicialices con README** (ya tenemos uno)
5. Click en "Create repository"

## Paso 2: Conectar repositorio local con GitHub

Una vez creado el repositorio en GitHub, ejecuta estos comandos:

```bash
# Agregar el remote de GitHub (reemplaza <USERNAME> con tu usuario)
git remote add origin https://github.com/<USERNAME>/project-ops.git

# O si prefieres SSH:
git remote add origin git@github.com:<USERNAME>/project-ops.git

# Verificar que se agregó correctamente
git remote -v

# Subir el código
git push -u origin master
```

## Paso 3: Configurar GitHub para desarrollo colaborativo

### Crear ramas de desarrollo
```bash
# Crear rama de desarrollo
git checkout -b develop
git push -u origin develop

# Crear rama para features
git checkout -b feature/nueva-funcionalidad
```

### Proteger rama master
En GitHub:
1. Settings → Branches → Add rule
2. Branch name pattern: `master`
3. ✅ Require pull request reviews before merging
4. ✅ Require status checks to pass before merging
5. Save changes

## Paso 4: Configurar GitHub Actions (CI/CD) - Opcional

Crear archivo `.github/workflows/docker.yml`:

```yaml
name: Docker Build and Test

on:
  push:
    branches: [ master, develop ]
  pull_request:
    branches: [ master ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: docker-compose build
    
    - name: Start services
      run: docker-compose up -d
    
    - name: Wait for services
      run: sleep 30
    
    - name: Check services
      run: docker-compose ps
    
    - name: Stop services
      run: docker-compose down
```

## Paso 5: Agregar badges al README (opcional)

Agregar al inicio del README.md:

```markdown
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/mysql-8.0-blue.svg?style=for-the-badge&logo=mysql&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
```

## Comandos útiles de Git

```bash
# Ver estado
git status

# Ver historial
git log --oneline

# Crear nueva rama
git checkout -b nombre-rama

# Cambiar de rama
git checkout nombre-rama

# Ver ramas
git branch -a

# Actualizar desde GitHub
git pull origin master

# Subir cambios
git add .
git commit -m "Descripción del cambio"
git push origin nombre-rama
```

## Flujo de trabajo recomendado

1. **Desarrollar en rama feature**
   ```bash
   git checkout -b feature/nueva-funcion
   # ... hacer cambios ...
   git add .
   git commit -m "Agregar nueva función"
   git push origin feature/nueva-funcion
   ```

2. **Crear Pull Request en GitHub**
   - Ir a GitHub
   - Click en "Compare & pull request"
   - Describir los cambios
   - Solicitar revisión

3. **Merge a develop y luego a master**
   ```bash
   # Después del merge en GitHub
   git checkout develop
   git pull origin develop
   
   # Cuando esté listo para producción
   git checkout master
   git merge develop
   git push origin master
   ```

## Mantener el repositorio actualizado

```bash
# Fetch cambios de todos
git fetch --all

# Ver diferencias
git diff master origin/master

# Actualizar tu rama actual
git pull origin master
```

## ⚠️ Archivos sensibles

El archivo `.gitignore` ya está configurado para excluir:
- ✅ `.env` (credenciales)
- ✅ `__pycache__/` (archivos temporales)
- ✅ `*.log` (logs)
- ✅ `venv/` (entorno virtual)

**NUNCA** subas al repositorio:
- ❌ Contraseñas en texto plano
- ❌ API keys
- ❌ Certificados SSL
- ❌ Datos de producción sensibles

## 🔒 Para proyectos privados

Si el código es sensible:
1. En GitHub, Settings → Danger Zone
2. Change repository visibility → Make private
3. Confirm

## 📦 Releases

Para crear versiones:
```bash
# Crear tag
git tag -a v1.0.0 -m "Primera versión estable"
git push origin v1.0.0
```

En GitHub → Releases → Draft a new release
