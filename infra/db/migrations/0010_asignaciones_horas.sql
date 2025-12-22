-- Migración: Cambiar dedicacion de porcentaje a horas
-- Fecha: 2025-12-22
-- Descripción: Cambia la columna dedicacion_pct a dedicacion_horas con máximo 160 horas

-- Renombrar la columna de dedicacion_pct a dedicacion_horas
ALTER TABLE asignaciones CHANGE COLUMN dedicacion_pct dedicacion_horas DECIMAL(5,2) NOT NULL DEFAULT 0;

-- Opcional: Si quieres convertir los porcentajes existentes a horas (asumiendo 160h = 100%)
-- UPDATE asignaciones SET dedicacion_horas = (dedicacion_horas / 100) * 160;
