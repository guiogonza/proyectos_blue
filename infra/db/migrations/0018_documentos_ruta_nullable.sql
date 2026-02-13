-- 0018_documentos_ruta_nullable.sql
-- Permitir crear anexos sin archivo físico asociado
ALTER TABLE documentos MODIFY COLUMN ruta_archivo VARCHAR(500) NULL DEFAULT NULL;
