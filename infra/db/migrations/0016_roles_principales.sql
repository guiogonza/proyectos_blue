-- Tabla para gestionar roles principales de personas de forma dinámica
CREATE TABLE IF NOT EXISTS roles_principales (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(200) NOT NULL UNIQUE,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar roles existentes
INSERT IGNORE INTO roles_principales (nombre) VALUES
  ('Technician I'),
  ('Technician II'),
  ('Experienced Technician I'),
  ('Experienced Technician II'),
  ('Technician specialist'),
  ('Technician architect');
