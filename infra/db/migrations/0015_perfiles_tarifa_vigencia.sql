-- Migración: Agregar campos tarifa_sin_iva y vigencia a la tabla perfiles
-- tarifa_sin_iva: valor monetario (DECIMAL) obligatorio para cada perfil
-- vigencia: fecha de vigencia (DATE) obligatoria para cada perfil

-- Agregar campo tarifa_sin_iva
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'perfiles' AND COLUMN_NAME = 'tarifa_sin_iva');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE perfiles ADD COLUMN tarifa_sin_iva DECIMAL(12,2) NULL AFTER nombre', 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar campo vigencia
SET @col_exists2 = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'perfiles' AND COLUMN_NAME = 'vigencia');
SET @sql2 = IF(@col_exists2 = 0, 'ALTER TABLE perfiles ADD COLUMN vigencia DATE NULL AFTER tarifa_sin_iva', 'SELECT 1');
PREPARE stmt2 FROM @sql2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;
