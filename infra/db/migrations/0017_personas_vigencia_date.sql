-- Migración: Cambiar tipo de dato de vigencia de INT a DATE en personas
-- También hacer campos obligatoriosNOT NULL: TIPO_DOCUMENTO, NUMERO_DOCUMENTO, PAIS

-- Modificar vigencia de INT a DATE
SET @col_type = (SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'personas' 
                AND COLUMN_NAME = 'vigencia');

-- Solo ejecutar si el tipo es INT (para evitar errores en re-ejecuciones)
SET @sql = IF(@col_type = 'int', 
    'ALTER TABLE personas MODIFY COLUMN vigencia DATE NULL',
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Hacer TIPO_DOCUMENTO NOT NULL (si existe y es NULL)
SET @col_exists_tipo = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                       WHERE TABLE_SCHEMA = DATABASE() 
                       AND TABLE_NAME = 'personas' 
                       AND COLUMN_NAME = 'TIPO_DOCUMENTO');
                       
SET @sql_tipo = IF(@col_exists_tipo > 0,
    'ALTER TABLE personas MODIFY COLUMN TIPO_DOCUMENTO VARCHAR(50) NOT NULL DEFAULT "Otro"',
    'SELECT 1');
PREPARE stmt_tipo FROM @sql_tipo;
EXECUTE stmt_tipo;
DEALLOCATE PREPARE stmt_tipo;

-- Hacer NUMERO_DOCUMENTO NOT NULL (si existe y es NULL)
SET @col_exists_num = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                      WHERE TABLE_SCHEMA = DATABASE() 
                      AND TABLE_NAME = 'personas' 
                      AND COLUMN_NAME = 'NUMERO_DOCUMENTO');
                      
SET @sql_num = IF(@col_exists_num > 0,
    'ALTER TABLE personas MODIFY COLUMN NUMERO_DOCUMENTO VARCHAR(50) NOT NULL DEFAULT ""',
    'SELECT 1');
PREPARE stmt_num FROM @sql_num;
EXECUTE stmt_num;
DEALLOCATE PREPARE stmt_num;

-- Hacer PAIS NOT NULL (si existe y es NULL)
SET @col_exists_pais = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                       WHERE TABLE_SCHEMA = DATABASE() 
                       AND TABLE_NAME = 'personas' 
                       AND COLUMN_NAME = 'PAIS');
                       
SET @sql_pais = IF(@col_exists_pais > 0,
    'ALTER TABLE personas MODIFY COLUMN PAIS VARCHAR(100) NOT NULL DEFAULT "Argentina"',
    'SELECT 1');
PREPARE stmt_pais FROM @sql_pais;
EXECUTE stmt_pais;
DEALLOCATE PREPARE stmt_pais;

-- Hacer vigencia NOT NULL con valor por defecto
-- Primero actualizar valores NULL existentes
UPDATE personas SET vigencia = CURRENT_DATE WHERE vigencia IS NULL;

-- Luego hacer la columna NOT NULL
SET @col_exists_vig = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                      WHERE TABLE_SCHEMA = DATABASE() 
                      AND TABLE_NAME = 'personas' 
                      AND COLUMN_NAME = 'vigencia');
                      
SET @sql_vig = IF(@col_exists_vig > 0,
    'ALTER TABLE personas MODIFY COLUMN vigencia DATE NOT NULL',
    'SELECT 1');
PREPARE stmt_vig FROM @sql_vig;
EXECUTE stmt_vig;
DEALLOCATE PREPARE stmt_vig;
