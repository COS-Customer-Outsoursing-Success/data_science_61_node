SELECT
    MAX(fecha_iniciada) AS hora_ultima_llamada
FROM bbdd_bigdata_smcc.tb_smcc_fidelizacion_detallado_casos
WHERE fecha_iniciada >= curdate()

