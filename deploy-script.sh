#!/bin/bash
# Script de despliegue automático para Project Ops
# Servidor: 164.68.118.86

set -e  # Detener si hay errores

echo "🚀 Iniciando despliegue de Project Ops..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker no encontrado. Instalando...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker instalado${NC}"
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose no encontrado. Instalando...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose instalado${NC}"
fi

# Crear directorio para la aplicación
APP_DIR="/opt/apps/project-ops"
echo -e "${YELLOW}Creando directorio de aplicación...${NC}"
sudo mkdir -p /opt/apps
sudo chown $USER:$USER /opt/apps

# Clonar o actualizar repositorio
if [ -d "$APP_DIR" ]; then
    echo -e "${YELLOW}Repositorio existe. Actualizando...${NC}"
    cd $APP_DIR
    git pull origin master
else
    echo -e "${YELLOW}Clonando repositorio...${NC}"
    cd /opt/apps
    git clone https://github.com/guiogonza/proyectos_blue.git project-ops
    cd project-ops
fi

echo -e "${GREEN}✅ Código descargado${NC}"

# Detener contenedores existentes si los hay
if [ "$(docker ps -q -f name=project_ops)" ]; then
    echo -e "${YELLOW}Deteniendo contenedores existentes...${NC}"
    docker-compose down
fi

# Limpiar contenedores y volúmenes antiguos (opcional)
# docker-compose down -v  # Descomentar si quieres limpiar volúmenes

# Iniciar servicios
echo -e "${YELLOW}Iniciando servicios con Docker Compose...${NC}"
docker-compose up -d

# Esperar a que MySQL esté listo
echo -e "${YELLOW}Esperando a que MySQL inicie...${NC}"
sleep 20

# Verificar que los contenedores estén corriendo
echo -e "${YELLOW}Verificando estado de contenedores...${NC}"
docker-compose ps

# Restaurar backup de base de datos
echo -e "${YELLOW}Restaurando base de datos...${NC}"
if docker exec -i project_ops_mysql mysql -uproject_ops_user -pproject_ops_pass project_ops < project_ops_backup.sql 2>/dev/null; then
    echo -e "${GREEN}✅ Base de datos restaurada${NC}"
else
    echo -e "${RED}⚠️  Error al restaurar base de datos (puede ser normal si ya existe)${NC}"
fi

# Mostrar logs
echo -e "${YELLOW}Mostrando logs (presiona Ctrl+C para salir)...${NC}"
sleep 2
docker-compose logs --tail=50 app

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ ¡Despliegue completado!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "📊 Accede a la aplicación en:"
echo -e "   ${YELLOW}http://164.68.118.86:8501${NC}"
echo ""
echo -e "👤 Credenciales por defecto:"
echo -e "   Email: ${YELLOW}admin@projectops.com${NC}"
echo -e "   Contraseña: ${YELLOW}admin123${NC}"
echo ""
echo -e "📝 Comandos útiles:"
echo -e "   Ver logs: ${YELLOW}docker-compose logs -f app${NC}"
echo -e "   Detener: ${YELLOW}docker-compose down${NC}"
echo -e "   Reiniciar: ${YELLOW}docker-compose restart app${NC}"
echo ""
