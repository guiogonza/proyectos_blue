-- Migración: Agregar tabla de perfiles y campo vigencia en personas
-- También añadir campo perfil_id en asignaciones

-- Tabla de perfiles
CREATE TABLE IF NOT EXISTS perfiles (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(200) NOT NULL UNIQUE,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agregar campo vigencia (año) en personas (ignorar error si ya existe)
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'personas' AND COLUMN_NAME = 'vigencia');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE personas ADD COLUMN vigencia INT NULL', 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar campo perfil_id en asignaciones (ignorar error si ya existe)
SET @col_exists2 = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'asignaciones' AND COLUMN_NAME = 'perfil_id');
SET @sql2 = IF(@col_exists2 = 0, 'ALTER TABLE asignaciones ADD COLUMN perfil_id BIGINT NULL', 'SELECT 1');
PREPARE stmt2 FROM @sql2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

-- Agregar FK si no existe
SET @fk_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'asignaciones' AND CONSTRAINT_NAME = 'fk_asignaciones_perfil');
SET @sql3 = IF(@fk_exists = 0, 'ALTER TABLE asignaciones ADD CONSTRAINT fk_asignaciones_perfil FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE SET NULL', 'SELECT 1');
PREPARE stmt3 FROM @sql3;
EXECUTE stmt3;
DEALLOCATE PREPARE stmt3;

-- Insertar perfiles predefinidos
INSERT INTO perfiles (nombre) VALUES
('Gerente'),
('Jefe de Proyecto Commodity'),
('Jefe de Proyecto Especial'),
('Analista Funcional / Orgánico JR Commodity'),
('Analista Funcional / Orgánico STD Commodity'),
('Analista Funcional / Orgánico SR Commodity'),
('Analista Funcional / Orgánico JR Especial'),
('Analista Funcional / Orgánico STD Especial'),
('Analista Funcional / Orgánico SR Especial'),
('Analista Programador / Programador JR Commodity'),
('Analista Programador / Programador STD Commodity'),
('Analista Programador / Programador SR Commodity'),
('Analista Programador / Programador JR Especial'),
('Analista Programador / Programador STD Especial'),
('Analista Programador / Programador SR Especial'),
('Consultor JR Commodity'),
('Consultor STD Commodity'),
('Consultor SR Commodity'),
('Consultor JR Especial'),
('Consultor STD Especial'),
('Consultor SR Especial'),
('Especialista STD Commodity'),
('Especialista STD Especial'),
('Agile Coach STD Especial'),
('Agile Coach SR Especial'),
('Scrum Master JR Especial'),
('Scrum Master STD Especial'),
('Scrum Master SR Especial'),
('Quality Assurance/Tester JR Commodity'),
('Quality Assurance/Tester STD Commodity'),
('Quality Assurance/Tester SR Commodity'),
('Quality Assurance/Tester JR Especial'),
('Quality Assurance/Tester STD Especial'),
('Quality Assurance/Tester SR Especial'),
('Arquitecto JR Especial'),
('Arquitecto STD Especial'),
('Arquitecto SR Especial'),
('Analista Banca Digital JR Especial'),
('Analista Banca Digital STD Especial'),
('Analista Banca Digital SR Especial'),
('UX/UI/Diseñador JR Especial'),
('UX/UI/Diseñador STD Especial'),
('UX/UI/Diseñador SR Especial'),
('Data Scientist JR Especial'),
('Data Scientist STD Especial'),
('Data Scientist SR Especial'),
('Data Engineer JR Especial'),
('Data Engineer STD Especial'),
('Data Engineer SR Especial'),
('Técnico JR Commodity'),
('Técnico STD Commodity'),
('Técnico SR Commodity'),
('Técnico JR Especial'),
('Técnico STD Especial'),
('Técnico SR Especial'),
('Administrador base de datos JR Commodity'),
('Administrador base de datos STD Commodity'),
('Administrador base de datos SR Commodity'),
('Administrador base de datos JR Especial'),
('Administrador base de datos STD Especial'),
('Administrador base de datos SR Especial'),
('PMO JR Commodity'),
('PMO STD Commodity'),
('PMO SR Commodity'),
('Proyecto Integral Commodity'),
('Proyecto Integral Especial'),
('Proyecto DYD Commodity'),
('Proyecto DYD Especial')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);
