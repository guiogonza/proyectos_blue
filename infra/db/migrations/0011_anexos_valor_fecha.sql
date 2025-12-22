-- Migración: Agregar campos valor y fecha_documento a anexos/documentos
-- Fecha: 2025-12-22
-- Descripción: Agrega campo valor (decimal) y fecha_documento a la tabla documentos

-- Agregar columna valor (acepta decimales)
ALTER TABLE documentos ADD COLUMN valor DECIMAL(15,2) NULL DEFAULT NULL;

-- Agregar columna fecha_documento (puede ser cualquier fecha)
ALTER TABLE documentos ADD COLUMN fecha_documento DATE NULL DEFAULT NULL;
