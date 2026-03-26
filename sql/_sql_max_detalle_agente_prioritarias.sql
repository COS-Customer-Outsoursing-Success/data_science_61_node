SELECT
    MAX(fecha_cargue) AS hora_ultima_llamada
FROM bbdd_cos_bog_claro_recuperacion.tb_detalle_agente_daily_new
WHERE fecha_cargue = CURDATE();
