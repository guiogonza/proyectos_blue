-- Migración 0008: Crear tabla de documentos para proyectos
CREATE TABLE IF NOT EXISTS documentos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    proyecto_id BIGINT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    descripcion TEXT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tamanio_bytes BIGINT NULL,
    tipo_mime VARCHAR(100) NULL,
    fecha_carga DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_documentos_proyecto (proyecto_id),
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
