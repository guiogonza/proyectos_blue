-- Migración: Agregar tabla de perfiles y campo vigencia en personas
-- También añadir campo perfil_id en asignaciones

-- Tabla de perfiles
CREATE TABLE IF NOT EXISTS perfiles (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(200) NOT NULL UNIQUE,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agregar campo vigencia (año) en personas
ALTER TABLE personas ADD COLUMN IF NOT EXISTS vigencia INT NULL;

-- Agregar campo perfil_id en asignaciones
ALTER TABLE asignaciones ADD COLUMN IF NOT EXISTS perfil_id BIGINT NULL;
ALTER TABLE asignaciones ADD CONSTRAINT fk_asignaciones_perfil 
  FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE SET NULL;

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
