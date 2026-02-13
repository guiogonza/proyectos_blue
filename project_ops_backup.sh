#!/bin/bash
# Backup diario de project_ops MySQL
BACKUP_DIR=/root/backups/project_ops
DATE=$(date +%Y%m%d_%H%M%S)
FILE=$BACKUP_DIR/project_ops_$DATE.sql.gz

# Crear backup comprimido
docker exec project_ops_mysql mysqldump --no-tablespaces -u project_ops_user -pproject_ops_pass project_ops 2>/dev/null | gzip > "$FILE"

if [ -s "$FILE" ]; then
    echo "[$(date)] Backup OK: $FILE ($(du -h "$FILE" | cut -f1))"
else
    echo "[$(date)] ERROR: Backup fallido o vacio"
    rm -f "$FILE"
fi

# Retener solo los ultimos 30 backups
cd "$BACKUP_DIR" && ls -t project_ops_*.sql.gz 2>/dev/null | tail -n +31 | xargs -r rm -f
