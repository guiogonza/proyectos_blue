-- 0019_documentos_id_sap.sql
-- Agregar campo ID_SAP a la tabla de documentos/anexos
ALTER TABLE documentos ADD COLUMN id_sap VARCHAR(50) NULL DEFAULT NULL AFTER fecha_documento;
CREATE INDEX idx_documentos_id_sap ON documentos(id_sap);
