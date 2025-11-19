-- Insertar personas
INSERT INTO personas (nombre, rol, tarifa_interna, cedula, numero_contacto, correo, activo) VALUES
('Juan Pérez', 'Desarrollador Senior', 80000.00, '1234567890', '555-0101', 'juan.perez@company.com', 1),
('María González', 'Diseñadora UX', 75000.00, '1234567891', '555-0102', 'maria.gonzalez@company.com', 1),
('Carlos Rodríguez', 'Arquitecto de Software', 95000.00, '1234567892', '555-0103', 'carlos.rodriguez@company.com', 1),
('Ana Martínez', 'QA Lead', 70000.00, '1234567893', '555-0104', 'ana.martinez@company.com', 1),
('Luis Hernández', 'Product Manager', 85000.00, '1234567894', '555-0105', 'luis.hernandez@company.com', 1);

-- Insertar proyectos
INSERT INTO proyectos (nombre, cliente, pm_id, fecha_inicio, fecha_fin_planeada, estado, costo_estimado_total) VALUES
('Sistema de Inventario', 'Empresa ABC', 3, '2024-01-15', '2024-06-30', 'Activo', 500000.00),
('App Mobile Banking', 'Banco XYZ', 5, '2024-02-01', '2024-08-31', 'Activo', 800000.00),
('Portal E-Learning', 'Universidad Nacional', 3, '2024-03-01', '2024-09-30', 'Activo', 350000.00);

-- Insertar sprints
INSERT INTO sprints (proyecto_id, nombre, fecha_inicio, fecha_fin, estado, costo_estimado) VALUES
(1, 'Sprint 1 - Setup', '2024-01-15', '2024-01-29', 'Cerrado', 50000.00),
(1, 'Sprint 2 - Core Features', '2024-01-30', '2024-02-13', 'En curso', 75000.00),
(2, 'Sprint 1 - Discovery', '2024-02-01', '2024-02-15', 'En curso', 60000.00);

-- Insertar asignaciones
INSERT INTO asignaciones (persona_id, proyecto_id, sprint_id, dedicacion_pct, fecha_asignacion, fecha_fin) VALUES
(1, 1, 2, 100.00, '2024-01-30', '2024-02-13'),
(2, 2, 3, 75.00, '2024-02-01', '2024-02-15'),
(3, 1, 2, 50.00, '2024-01-30', '2024-02-13'),
(4, 1, 2, 87.50, '2024-01-30', '2024-02-13'),
(5, 2, 3, 37.50, '2024-02-01', '2024-02-15');
