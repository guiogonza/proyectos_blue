SELECT 'all_budget' as scope, SUM(BUDGET) as val, COUNT(*) as n FROM proyectos;
SELECT 'active_2026' as scope, SUM(BUDGET) as val, COUNT(*) as n FROM proyectos WHERE ESTADO='Activo' AND FECHA_INICIO <= '2026-12-31' AND FECHA_FIN_ESTIMADA >= '2026-01-01';
SELECT 'anx_2026' as scope, SUM(valor) as val, COUNT(*) as n FROM documentos WHERE valor > 0 AND fecha_documento BETWEEN '2026-01-01' AND '2026-12-31';
SELECT 'anx_all' as scope, SUM(valor) as val, COUNT(*) as n FROM documentos WHERE valor > 0;
SELECT 'costo_2026' as scope, SUM(a.dedicacion_horas * p.COSTO_RECURSO) as val, COUNT(*) as n FROM asignaciones a JOIN personas p ON p.id=a.persona_id WHERE a.fecha_asignacion <= '2026-12-31' AND (a.fecha_fin IS NULL OR a.fecha_fin >= '2026-01-01');
