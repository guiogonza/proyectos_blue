-- Script para migrar vigencia de INT a DATE de manera segura
-- Paso 1: Actualizar NULL a fecha actual
UPDATE personas 
SET vigencia = CURRENT_DATE
WHERE vigencia IS NULL;

-- Paso 2: Convertir años a fechas (2026 -> 2026-01-01)
UPDATE personas 
SET vigencia = STR_TO_DATE(CONCAT(vigencia, '-01-01'), '%Y-%m-%d')
WHERE vigencia REGEXP '^[0-9]{4}$';

-- Paso 3: Modificar el tipo de columna de VARCHAR a DATE
ALTER TABLE personas MODIFY COLUMN vigencia DATE NOT NULL;

-- Paso 4: Actualizar valores NULL antes de hacer campos obligatorios
UPDATE personas SET TIPO_DOCUMENTO = 'Otro' WHERE TIPO_DOCUMENTO IS NULL;
UPDATE personas SET NUMERO_DOCUMENTO = '' WHERE NUMERO_DOCUMENTO IS NULL;
UPDATE personas SET PAIS = 'Argentina' WHERE PAIS IS NULL;

-- Paso 5: Hacer otros campos obligatorios
ALTER TABLE personas MODIFY COLUMN TIPO_DOCUMENTO VARCHAR(50) NOT NULL DEFAULT 'Otro';
ALTER TABLE personas MODIFY COLUMN NUMERO_DOCUMENTO VARCHAR(50) NOT NULL DEFAULT '';
ALTER TABLE personas MODIFY COLUMN PAIS VARCHAR(100) NOT NULL DEFAULT 'Argentina';
