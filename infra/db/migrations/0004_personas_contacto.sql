-- Migración para agregar campos de contacto a personas
-- 0004_personas_contacto.sql

-- Agregar campos de cédula, número de contacto y correo a la tabla personas
ALTER TABLE personas 
ADD COLUMN cedula VARCHAR(20) NULL AFTER tarifa_interna,
ADD COLUMN numero_contacto VARCHAR(15) NULL AFTER cedula,
ADD COLUMN correo VARCHAR(100) NULL AFTER numero_contacto;

-- Crear índices para búsqueda rápida
CREATE INDEX idx_personas_cedula ON personas(cedula);
CREATE INDEX idx_personas_correo ON personas(correo);