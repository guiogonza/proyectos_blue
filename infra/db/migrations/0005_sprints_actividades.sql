-- Migración para agregar campo actividades a sprints
-- 0005_sprints_actividades.sql

-- Agregar campo de actividades a la tabla sprints
ALTER TABLE sprints 
ADD COLUMN actividades TEXT NULL AFTER estado;

-- Agregar índice para búsqueda de texto si es necesario
CREATE FULLTEXT INDEX idx_sprints_actividades ON sprints(actividades);