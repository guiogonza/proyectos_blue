USE project_ops;

CREATE TABLE IF NOT EXISTS sprints (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  proyecto_id       INT NOT NULL,
  nombre            VARCHAR(120) NOT NULL,
  fecha_inicio      DATE NOT NULL,
  fecha_fin         DATE NOT NULL,
  costo_estimado    DECIMAL(16,2) NOT NULL DEFAULT 0,
  costo_real        DECIMAL(16,2) NULL,
  estado            ENUM('Planificado','En curso','Cerrado') NOT NULL DEFAULT 'Planificado',
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_sprint_proyecto FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE,
  INDEX idx_sprints_proyecto (proyecto_id),
  INDEX idx_sprints_estado (estado)
);
