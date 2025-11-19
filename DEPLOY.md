# 🚀 Guía de Despliegue en Host Remoto

## Opción 1: Servidor con Docker (Recomendado)

### Prerrequisitos en el servidor
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Docker y Docker Compose instalados
- Git instalado
- Puerto 8501 abierto en firewall

### Pasos de instalación

1. **Conectar al servidor**
```bash
ssh usuario@tu-servidor.com
```

2. **Instalar Docker y Docker Compose (si no están instalados)**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar sesión para aplicar cambios
exit
```

3. **Clonar el repositorio**
```bash
cd /opt
sudo mkdir -p apps
sudo chown $USER:$USER apps
cd apps
git clone <URL_DE_TU_REPOSITORIO> project-ops
cd project-ops
```

4. **Configurar variables de entorno (opcional)**
```bash
# Crear archivo .env para producción
cat > .env << EOF
ENV=production
DEBUG=false
APP_SECRET_KEY=$(openssl rand -hex 32)
DB_HOST=mysql
DB_PORT=3306
DB_NAME=project_ops
DB_USER=project_ops_user
DB_PASSWORD=$(openssl rand -base64 32)
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32)
TZ=America/Bogota
EOF
```

5. **Iniciar los contenedores**
```bash
docker-compose up -d
```

6. **Verificar que todo esté funcionando**
```bash
docker-compose ps
docker-compose logs -f app
```

7. **Restaurar backup de base de datos**
```bash
docker exec -i project_ops_mysql mysql -uproject_ops_user -pproject_ops_pass project_ops < project_ops_backup.sql
```

8. **Configurar Nginx como reverse proxy (opcional pero recomendado)**
```bash
sudo apt install nginx -y

# Crear configuración de Nginx
sudo nano /etc/nginx/sites-available/project-ops
```

Agregar:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Activar sitio:
```bash
sudo ln -s /etc/nginx/sites-available/project-ops /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

9. **Configurar SSL con Let's Encrypt (opcional)**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tu-dominio.com
```

10. **Configurar inicio automático**
```bash
# Docker Compose se inicia automáticamente con systemd
sudo systemctl enable docker
```

---

## Opción 2: Servidor sin Docker (Python directo)

### Prerrequisitos
- Python 3.11+
- MySQL 8.0
- Nginx (opcional)

### Pasos

1. **Instalar dependencias del sistema**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip mysql-server nginx -y
```

2. **Configurar MySQL**
```bash
sudo mysql_secure_installation
sudo mysql

# En MySQL:
CREATE DATABASE project_ops;
CREATE USER 'project_ops_user'@'localhost' IDENTIFIED BY 'tu_password_segura';
GRANT ALL PRIVILEGES ON project_ops.* TO 'project_ops_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

3. **Clonar repositorio**
```bash
cd /opt/apps
git clone <URL_REPOSITORIO> project-ops
cd project-ops
```

4. **Crear entorno virtual e instalar dependencias**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Configurar variables de entorno**
```bash
cat > .env << EOF
ENV=production
DEBUG=false
APP_SECRET_KEY=$(openssl rand -hex 32)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=project_ops
DB_USER=project_ops_user
DB_PASSWORD=tu_password_segura
TZ=America/Bogota
EOF
```

6. **Ejecutar migraciones**
```bash
mysql -u project_ops_user -p project_ops < infra/db/migrations/0001_init.sql
mysql -u project_ops_user -p project_ops < infra/db/migrations/0004_personas_contacto.sql
mysql -u project_ops_user -p project_ops < infra/db/migrations/0005_sprints_actividades.sql
mysql -u project_ops_user -p project_ops < project_ops_backup.sql
```

7. **Crear servicio systemd**
```bash
sudo nano /etc/systemd/system/project-ops.service
```

Agregar:
```ini
[Unit]
Description=Project Ops Streamlit Application
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/apps/project-ops
Environment="PATH=/opt/apps/project-ops/venv/bin"
ExecStart=/opt/apps/project-ops/venv/bin/streamlit run apps/dashboard/main.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

8. **Iniciar servicio**
```bash
sudo systemctl daemon-reload
sudo systemctl enable project-ops
sudo systemctl start project-ops
sudo systemctl status project-ops
```

---

## 🔒 Configuración de Seguridad Adicional

### Firewall
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Backup automatizado
```bash
# Crear script de backup
sudo nano /opt/scripts/backup-project-ops.sh
```

Contenido:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/project-ops"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup de base de datos
docker exec project_ops_mysql mysqldump -uproject_ops_user -pproject_ops_pass --no-tablespaces project_ops > $BACKUP_DIR/db_backup_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Eliminar backups antiguos (más de 7 días)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

Hacer ejecutable y agregar a crontab:
```bash
sudo chmod +x /opt/scripts/backup-project-ops.sh
crontab -e
# Agregar: 0 2 * * * /opt/scripts/backup-project-ops.sh
```

---

## 📊 Monitoreo

### Ver logs
```bash
# Docker
docker-compose logs -f app
docker-compose logs -f mysql

# Servicio systemd
sudo journalctl -u project-ops -f
```

### Estadísticas de recursos
```bash
docker stats
```

---

## 🔄 Actualización del código

```bash
cd /opt/apps/project-ops
git pull origin main
docker-compose restart app
# O si no usas Docker:
sudo systemctl restart project-ops
```

---

## 🆘 Solución de Problemas

### La aplicación no inicia
```bash
# Ver logs
docker-compose logs app
# O
sudo journalctl -u project-ops -f
```

### Base de datos no conecta
```bash
# Verificar que MySQL esté corriendo
docker-compose ps mysql
# Verificar credenciales en docker-compose.yml
```

### Puerto 8501 ya en uso
```bash
# Encontrar proceso
sudo lsof -i :8501
# Matar proceso
sudo kill -9 <PID>
```

---

## 📞 Acceso a la aplicación

- **Local**: http://localhost:8501
- **Servidor**: http://tu-servidor.com (o IP del servidor)
- **Con dominio y SSL**: https://tu-dominio.com

**Credenciales por defecto:**
- Email: `admin@projectops.com`
- Contraseña: `admin123`

⚠️ **IMPORTANTE**: Cambiar las contraseñas por defecto después del primer login.
