-- Esquema inicial mínimo (ajustable)
CREATE TABLE IF NOT EXISTS personas (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(200) NOT NULL,
  rol VARCHAR(100) NOT NULL,
  tarifa_interna DECIMAL(14,2) NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proyectos (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(200) NOT NULL,
  cliente VARCHAR(200) NULL,
  pm_id BIGINT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin_planeada DATE NOT NULL,
  estado VARCHAR(50) NOT NULL DEFAULT 'Borrador',
  costo_estimado_total DECIMAL(16,2) NOT NULL DEFAULT 0,
  costo_real_total DECIMAL(16,2) NULL,
  baseline_fecha DATETIME NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (pm_id) REFERENCES personas(id)
);

CREATE TABLE IF NOT EXISTS sprints (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  proyecto_id BIGINT NOT NULL,
  nombre VARCHAR(200) NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  estado VARCHAR(50) NOT NULL DEFAULT 'Planificado',
  costo_estimado DECIMAL(16,2) NOT NULL DEFAULT 0,
  costo_real DECIMAL(16,2) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX (proyecto_id),
  FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
);

CREATE TABLE IF NOT EXISTS asignaciones (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  persona_id BIGINT NOT NULL,
  proyecto_id BIGINT NOT NULL,
  sprint_id BIGINT NULL,
  dedicacion_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
  fecha_asignacion DATE NOT NULL,
  fecha_fin DATE NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX (persona_id),
  INDEX (proyecto_id),
  FOREIGN KEY (persona_id) REFERENCES personas(id),
  FOREIGN KEY (proyecto_id) REFERENCES proyectos(id),
  FOREIGN KEY (sprint_id) REFERENCES sprints(id)
);

CREATE TABLE IF NOT EXISTS usuarios (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(200) NOT NULL UNIQUE,
  hash_password VARCHAR(255) NOT NULL,
  rol_app VARCHAR(50) NOT NULL,
  persona_id BIGINT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  ultimo_login DATETIME NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (persona_id) REFERENCES personas(id)
);

CREATE TABLE IF NOT EXISTS parametros (
  clave VARCHAR(100) PRIMARY KEY,
  valor VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS event_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actor_id BIGINT NULL,
  tipo VARCHAR(100) NOT NULL,
  entidad VARCHAR(100) NOT NULL,
  entidad_id BIGINT NULL,
  detalle JSON NULL
);
