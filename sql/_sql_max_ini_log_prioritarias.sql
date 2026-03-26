SELECT
    MAX(sp.hora_log_ini_turn) AS hora_ultima_llamada

FROM bbdd_config.tb_soul_proglog sp
         INNER JOIN bbdd_config.tb_headcount hc ON sp.documento = hc.documento
WHERE Campana = 'Claro - Prioritarias Tercer Anillo'
  AND Estado = 'Activo'
  AND Cargo = 'Asesor'
  AND sp.fecha_prog_ini_turn = CURDATE()