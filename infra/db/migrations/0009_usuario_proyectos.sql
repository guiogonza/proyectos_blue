-- Migración: Asignación de proyectos a usuarios
-- Permite que usuarios no-admin solo vean sus proyectos asignados

CREATE TABLE IF NOT EXISTS usuario_proyectos (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  usuario_id BIGINT NOT NULL,
  proyecto_id BIGINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_usuario_proyecto (usuario_id, proyecto_id),
  INDEX (usuario_id),
  INDEX (proyecto_id),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE
);
