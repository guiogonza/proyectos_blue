-- Agregar campo tarifa en asignaciones
-- Campo opcional para almacenar la tarifa por hora de la asignación

SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'asignaciones' AND COLUMN_NAME = 'tarifa');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE asignaciones ADD COLUMN tarifa DECIMAL(10,2) NULL AFTER dedicacion_horas', 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
