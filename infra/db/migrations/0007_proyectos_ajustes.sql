-- Migración 0007: Reestructurar tabla proyectos
-- Renombrar columnas y agregar nuevos campos según especificaciones

-- Renombrar columnas existentes
ALTER TABLE proyectos 
    CHANGE COLUMN nombre NOMBRE VARCHAR(200) NOT NULL,
    CHANGE COLUMN fecha_inicio FECHA_INICIO DATE NOT NULL,
    CHANGE COLUMN fecha_fin_planeada FECHA_FIN_ESTIMADA DATE NOT NULL,
    CHANGE COLUMN estado ESTADO VARCHAR(50) NOT NULL DEFAULT 'Activo',
    CHANGE COLUMN costo_estimado_total BUDGET DECIMAL(14,2) NULL,
    CHANGE COLUMN costo_real_total COSTO_REAL_TOTAL DECIMAL(14,2) NULL;

-- Agregar nuevos campos
ALTER TABLE proyectos
    ADD COLUMN PAIS VARCHAR(100) NULL AFTER BUDGET,
    ADD COLUMN CATEGORIA VARCHAR(100) NULL AFTER PAIS,
    ADD COLUMN LIDER_BLUETAB VARCHAR(200) NULL AFTER CATEGORIA,
    ADD COLUMN LIDER_CLIENTE VARCHAR(200) NULL AFTER LIDER_BLUETAB,
    ADD COLUMN FECHA_FIN DATE NULL AFTER LIDER_CLIENTE,
    ADD COLUMN MANAGER_BLUETAB VARCHAR(200) NULL AFTER FECHA_FIN;

-- NOTA: NO renombramos 'id' porque causaría problemas con las FKs en asignaciones y sprints
-- Mantenemos 'id' como está para compatibilidad con las relaciones existentes
