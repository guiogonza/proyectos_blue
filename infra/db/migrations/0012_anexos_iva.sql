-- Migración: Agregar campo IVA a anexos/documentos
-- Fecha: 2025-12-22
-- Descripción: Agrega campo iva (decimal) a la tabla documentos

ALTER TABLE documentos ADD COLUMN iva DECIMAL(15,2) NULL DEFAULT NULL AFTER valor;
