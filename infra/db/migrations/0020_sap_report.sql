-- 0020_sap_report.sql
-- Crear tabla para almacenar reportes SAP de horas
CREATE TABLE IF NOT EXISTS sap_report (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nro INT NULL,
    id_empleado_sap VARCHAR(50) NULL,
    colaborador VARCHAR(200) NOT NULL,
    id_sap VARCHAR(50) NOT NULL,
    proyecto_sap VARCHAR(300) NOT NULL,
    horas_mes DECIMAL(10,2) NOT NULL DEFAULT 0,
    mes VARCHAR(20) NOT NULL,
    anio INT NOT NULL DEFAULT 2026,
    tipo_novedad VARCHAR(100) NULL,
    tiempo_novedad_hrs DECIMAL(10,2) NULL,
    reporte_sap TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sap_colaborador (colaborador),
    INDEX idx_sap_id_sap (id_sap),
    INDEX idx_sap_mes_anio (mes, anio),
    INDEX idx_sap_id_empleado (id_empleado_sap)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
