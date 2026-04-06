#!/usr/bin/env python3
"""
project_ops_backup.py
Backup diario de Project Ops (Colombia + Perú)
- Dump SQL comprimido de cada BD
- Retención: 7 días locales
- Copia opcional a almacenamiento externo (rclone / scp)
"""
import subprocess, os, datetime, glob, sys, logging

# ── Configuración ─────────────────────────────────────────────────────────────
BACKUP_DIR   = "/root/backups/project_ops"
RETENTION_DAYS = 7
DATE         = datetime.datetime.now().strftime("%Y%m%d_%H%M")

# Subida a Google Drive (requiere rclone + rclone config con remote llamado "gdrive")
GDRIVE_REMOTE = "gdrive:backups/project_ops"   # carpeta en Drive
GDRIVE_ENABLED = True                           # cambiar a False para deshabilitar

DATABASES = [
    {
        "label":     "colombia",
        "container": "project_ops_mysql",
        "db":        "project_ops",
        "user":      "root",
        "password":  "rootpass",
    },
    {
        "label":     "peru",
        "container": "project_ops_mysql_peru",
        "db":        "project_ops_peru",
        "user":      "root",
        "password":  "rootpass_peru",
    },
]

# Directorio de uploads (archivos adjuntos)
UPLOADS_DIR  = "/root/project-ops/uploads"

# ── Logging ───────────────────────────────────────────────────────────────────
os.makedirs(BACKUP_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(BACKUP_DIR, "backup.log"),
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
log = logging.getLogger()

def run(cmd, **kw):
    r = subprocess.run(cmd, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return r

errors = []

# ── 1. Dump SQL de cada BD ─────────────────────────────────────────────────────
for db in DATABASES:
    out_file = os.path.join(BACKUP_DIR, f"db_{db['label']}_{DATE}.sql.gz")
    log.info(f"Backup BD {db['label']} → {out_file}")
    try:
        dump = subprocess.Popen(
            ["docker", "exec", db["container"],
             "mysqldump", f"-u{db['user']}", f"-p{db['password']}",
             "--no-tablespaces", "--single-transaction", db["db"]],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        import gzip
        with gzip.open(out_file, "wb") as gz:
            gz.write(dump.stdout.read())
        dump.wait()
        if dump.returncode != 0:
            raise RuntimeError(dump.stderr.read().decode())
        size = os.path.getsize(out_file)
        log.info(f"  OK  {size/1024:.1f} KB")
    except Exception as e:
        log.error(f"  ERROR: {e}")
        errors.append(f"db_{db['label']}: {e}")

# ── 2. Backup de uploads (archivos adjuntos) ──────────────────────────────────
uploads_out = os.path.join(BACKUP_DIR, f"uploads_{DATE}.tar.gz")
log.info(f"Backup uploads → {uploads_out}")
try:
    run(["tar", "-czf", uploads_out, "-C", os.path.dirname(UPLOADS_DIR),
         os.path.basename(UPLOADS_DIR)])
    size = os.path.getsize(uploads_out)
    log.info(f"  OK  {size/1024:.1f} KB")
except Exception as e:
    log.error(f"  ERROR uploads: {e}")
    errors.append(f"uploads: {e}")

# ── 3. Purgar backups antiguos ────────────────────────────────────────────────
cutoff = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
for f in glob.glob(os.path.join(BACKUP_DIR, "*.gz")):
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(f))
    if mtime < cutoff:
        os.remove(f)
        log.info(f"Purgado: {f}")

# ── 4. Subir a Google Drive ───────────────────────────────────────────────────
if GDRIVE_ENABLED:
    log.info(f"Subiendo backups a Google Drive → {GDRIVE_REMOTE}")
    try:
        run(["rclone", "copy", BACKUP_DIR, GDRIVE_REMOTE,
             "--include", f"*_{DATE}*.gz",     # solo los de hoy
             "--drive-use-trash=false"])
        log.info("  OK: archivos subidos a Drive")
    except Exception as e:
        log.error(f"  ERROR Google Drive: {e}")
        errors.append(f"gdrive: {e}")

# ── 5. Resumen ─────────────────────────────────────────────────────────────────
if errors:
    log.error(f"Backup finalizado con errores: {errors}")
    sys.exit(1)
else:
    log.info("Backup completado correctamente.")
    print("OK")
