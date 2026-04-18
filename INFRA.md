# Project Ops — Infraestructura Multi-País

> Servidor VPS: `164.68.118.86`  
> Última actualización: 6 de abril de 2026

---

## URLs de acceso

| Servicio | Colombia 🇨🇴 | Perú 🇵🇪 |
|---|---|---|
| **Dashboard** (Streamlit) | http://164.68.118.86/colombia | http://164.68.118.86/peru |
| **API REST** (FastAPI) | http://164.68.118.86/colombia-api/ | http://164.68.118.86/peru-api/ |
| **Swagger UI** | http://164.68.118.86/colombia-api/docs | http://164.68.118.86/peru-api/docs |
| **ReDoc** | http://164.68.118.86/colombia-api/redoc | http://164.68.118.86/peru-api/redoc |
| **OpenAPI JSON** | http://164.68.118.86/colombia-api/openapi.json | http://164.68.118.86/peru-api/openapi.json |

> La API es **solo lectura** (métodos GET). Requiere autenticación HTTP Basic con las mismas credenciales del dashboard.

---

## Arquitectura de contenedores

```
VPS 164.68.118.86
│
├── Nginx (puerto 80)  ──routes──►
│     /colombia     → project_ops_app      :8501
│     /colombia-api → project_ops_api      :8502
│     /peru         → project_ops_app_peru :8510
│     /peru-api     → project_ops_api_peru :8511
│
├── project_ops_mysql      (MySQL 8, puerto ext. 3312)  ← BD Colombia
├── project_ops_app        (Streamlit, puerto 8501)
├── project_ops_api        (FastAPI,   puerto 8502)
│
├── project_ops_mysql_peru (MySQL 8, puerto ext. 3311)  ← BD Perú
├── project_ops_app_peru   (Streamlit, puerto 8510)
└── project_ops_api_peru   (FastAPI,   puerto 8511)
```

### Variables de entorno por país

| Variable | Colombia | Perú |
|---|---|---|
| `COUNTRY` | `colombia` | `peru` |
| `TZ` | `America/Bogota` | `America/Lima` |
| `DB_NAME` | `project_ops` | `project_ops_peru` |
| `API_ROOT_PATH` | `/colombia-api` | `/peru-api` |

---

## Gestión de contenedores

### Iniciar / detener Colombia
```bash
cd /root/project-ops
docker compose up -d                          # Iniciar todo
docker compose up -d --no-deps app            # Solo dashboard
docker compose up -d --no-deps api            # Solo API
docker compose down                           # Detener todo
```

### Iniciar / detener Perú
```bash
cd /root/project-ops
docker compose -f docker-compose.peru.yml --env-file .env.peru up -d
docker compose -f docker-compose.peru.yml --env-file .env.peru down
```

### Ver logs en tiempo real
```bash
docker logs -f project_ops_app               # Dashboard Colombia
docker logs -f project_ops_app_peru          # Dashboard Perú
docker logs -f project_ops_api               # API Colombia
docker logs -f project_ops_api_peru          # API Perú
```

### Checklist post-deploy (Nginx + Docker)
```bash
cd /root/project-ops
chmod +x post_deploy_check.sh
./post_deploy_check.sh
```

Para validar contra otro host/IP:
```bash
./post_deploy_check.sh 164.68.118.86
```

---

## Archivos de configuración

| Archivo | Descripción |
|---|---|
| `docker-compose.yml` | Stack Colombia |
| `docker-compose.peru.yml` | Stack Perú |
| `.env.colombia` | Variables de entorno Colombia |
| `.env.peru` | Variables de entorno Perú |
| `shared/config.py` | Lee `COUNTRY` del entorno |
| `apps/dashboard/pages/00_Login.py` | Login con bandera por país |
| `apps/api/main.py` | API FastAPI con `root_path` dinámico |

---

## Backups

### Script principal
**Ubicación en servidor:** `/root/project_ops_backup.py`  
**Directorio de backups:** `/root/backups/project_ops/`

### Qué se respalda
| Archivo generado | Contenido |
|---|---|
| `db_colombia_YYYYMMDD_HHMM.sql.gz` | Dump completo BD Colombia (comprimido) |
| `db_peru_YYYYMMDD_HHMM.sql.gz` | Dump completo BD Perú (comprimido) |
| `uploads_YYYYMMDD_HHMM.tar.gz` | Archivos adjuntos (documentos subidos) |
| `backup.log` | Log de todos los backups ejecutados |

### Retención
- **7 días** de backups locales  
- Los archivos más antiguos se purgan automáticamente

### Cron (2:00 AM todos los días)
```
0 2 * * * python3 /root/project_ops_backup.py >> /root/backups/project_ops/cron.log 2>&1
```

### Ejecutar backup manual
```bash
python3 /root/project_ops_backup.py
```

### Restaurar una BD desde backup
```bash
# Colombia
gunzip -c /root/backups/project_ops/db_colombia_YYYYMMDD_HHMM.sql.gz \
  | docker exec -i project_ops_mysql mysql -uroot -prootpass project_ops

# Perú
gunzip -c /root/backups/project_ops/db_peru_YYYYMMDD_HHMM.sql.gz \
  | docker exec -i project_ops_mysql_peru mysql -uroot -prootpass_peru project_ops_peru
```

---

## Opciones de backup externo (ante falla del VPS)

### Opción A — Backblaze B2 (recomendada, gratuita hasta 10 GB)
```bash
# 1. Instalar rclone
curl https://rclone.org/install.sh | bash

# 2. Configurar (sigue el wizard)
rclone config  # tipo: b2, ingresa App Key ID y App Key

# 3. Agregar al script de backup (en project_ops_backup.py):
#    subprocess.run(["rclone", "copy", BACKUP_DIR, "b2:mi-bucket/project_ops"])

# 4. Cron alternativo que también sube a B2
0 2 * * * python3 /root/project_ops_backup.py && rclone copy /root/backups/project_ops b2:mi-bucket/project_ops --max-age 7d
```
**Costo:** $0 (primeros 10 GB gratis, luego ~$0.006/GB/mes)

### Opción B — Google Drive (rclone gdrive)
```bash
rclone config   # tipo: drive, autoriza con cuenta Google
# Sube igual que B2:
rclone copy /root/backups/project_ops gdrive:backups/project_ops
```
**Costo:** $0 (15 GB gratis en cuenta personal)

### Opción C — Otro servidor / PC local (rsync + SSH)
```bash
# Desde el VPS hacia otro servidor con clave SSH ya configurada:
rsync -az --delete /root/backups/project_ops/ usuario@ip-destino:/backups/project_ops/
```
**Requiere:** servidor de destino accesible por SSH

### Opción D — Hetzner Storage Box (más confiable)
```bash
# Montar con SSHFS o usar rsync hacia storage.hetzner.com
rsync -az /root/backups/project_ops/ uXXXXXX@uXXXXXX.your-storagebox.de:/home/backups/
```
**Costo:** ~€3.8/mes por 100 GB (misma región del VPS, alta velocidad)

---

## Recuperación ante falla total del VPS

1. Provisionar nuevo VPS con Ubuntu 22.04+
2. Instalar Docker y Docker Compose
3. Clonar el repositorio del proyecto
4. Copiar los `.env.colombia` y `.env.peru`
5. Levantar los stacks:
   ```bash
   docker compose up -d
   docker compose -f docker-compose.peru.yml --env-file .env.peru up -d
   ```
6. Restaurar las BDs desde el último backup (ver sección "Restaurar" arriba)
7. Copiar archivos de uploads restaurando el `tar.gz`
8. Actualizar Nginx con el archivo `/etc/nginx/sites-enabled/gitea-bare-ip`

**RTO estimado:** ~30 minutos  
**RPO (pérdida máxima de datos):** 24 horas (un día de operaciones)

---

## Credenciales MySQL

| Instancia | Usuario | Password | Puerto externo |
|---|---|---|---|
| Colombia | `root` | `rootpass` | `3312` |
| Perú | `root` | `rootpass_peru` | `3311` |

> ⚠️ Cambiar las contraseñas en producción actualizando los archivos `.env.*` y recreando los contenedores.
