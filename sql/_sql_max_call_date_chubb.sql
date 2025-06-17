SELECT 
MAX(call_date) AS hora_ultima_llamada
FROM bbdd_bigdata_marcaciones_vicidial.tb_marcaciones_vicidial_out_chubb
WHERE call_date >= curdate()