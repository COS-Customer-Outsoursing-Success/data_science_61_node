create
    definer = jhonersalcedo1672@`10.206.158.36` procedure sp_16_depurador_gopass()
BEGIN

    SET @_fecha = CURDATE();
    SET @FECHA_GESTION = SUBDATE(CURDATE(), 30);
    SET @day_ini = CONCAT(SUBDATE(CURDATE(), 30), ' 00:00:00');
    SET @date_day = DATE_FORMAT(CURDATE(), '%Y-%m-01');
    SET @last_day = LAST_DAY(CURDATE());
    SET @datetime_day = DATE_FORMAT(CURDATE(), '%Y-%m-01 00:00:00');
    SET @datetime_lastday = DATE_FORMAT(LAST_DAY(CURDATE()), '%Y-%m-%d 23:59:59');

    -- LIMITE DE REGISTROS A PROCESAR
    SET @LIMITE_REGISTROS = 70000;

    TRUNCATE TABLE bbdd_cos_bog_gopass.tb_depurado_go_pass;

#################################### CARGA NUMEROS ASIGNACION GOPASS - LIMITADA Y PRIORIZADA #############################################
    INSERT INTO bbdd_cos_bog_gopass.tb_depurado_go_pass
    (Celular, Cuenta, Estado, Doc, deuda, balance, nombres_apellidos, correo, tipo, membresia, fecha_asignacion, fecha_ano_mes, Fecha_carga)
    SELECT
        sub.celular,
        sub.cuenta,
        sub.estado,
        sub.doc,
        sub.deuda,
        sub.balance,
        sub.nombres_apellidos,
        sub.correo,
        sub.tipo,
        sub.membresia,
        sub.fecha_asignacion,
        sub.fecha_ano_mes,
        @_fecha AS Fecha_carga
    FROM (
             SELECT
                 celular,
                 MAX(cuenta) AS cuenta,
                 MAX(estado) AS estado,
                 doc,
                 MAX(deuda) AS deuda,
                 MAX(balance) AS balance,
                 MAX(CONCAT(nombres, ' ', apellidos)) AS nombres_apellidos,
                 MAX(correo) AS correo,
                 MAX(tipo) AS tipo,
                 MAX(membresia) AS membresia,
                 MAX(fecha_asignacion) AS fecha_asignacion,
                 MAX(fecha_ano_mes) AS fecha_ano_mes,
                 ROW_NUMBER() OVER(ORDER BY MAX(deuda) DESC, celular) AS rn
             FROM bbdd_cos_bog_gopass.tb_asignacion_cobranza_gopass
             WHERE LENGTH(celular) = 10
               AND celular REGEXP '^3[0-9]{9}$'
               AND celular != REPEAT(SUBSTRING(celular, 1, 1), CHAR_LENGTH(celular))
               AND fecha_asignacion = @_fecha
               AND membresia NOT LIKE '%Membresía B2B%'
               AND estado = 'Suspendido por Saldo o Metodo de Pago'
             GROUP BY celular, doc
         ) sub
    WHERE sub.rn <= @LIMITE_REGISTROS;

#################################### ACTUALIZA PAGOS CRM Y ZEUS GOPASS - OPTIMIZADA #####################################
    UPDATE bbdd_cos_bog_gopass.tb_depurado_go_pass i
        INNER JOIN (
            SELECT
                celular,
                MAX(fecha_recaudo) AS fecha_recaudo,
                MAX(servicio) AS servicio,
                SUM(valor) AS valor,
                COUNT(*) AS cant_recaudo
            FROM (
                     SELECT
                         sac.tosac_fk_tipo_dato AS celular,
                         DATE(sac.tosac_fecha) AS fecha_recaudo,
                         CASE
                             WHEN cl2.tvcn2_tipo = 'RECARGA' THEN 'Recargas'
                             WHEN cl2.tvcn2_tipo = 'RECOBRO POR USUARIO' THEN 'Recobro Por Usuario'
                             ELSE 'Otro Medio'
                             END AS servicio,
                         CAST(TRIM(SUBSTRING_INDEX(sac.tosac_detalle, '//', 1)) AS DECIMAL(15,2)) AS valor
                     FROM bbdd_bigdata_rpa.tb_operacion_sac_crm_allinonegopass_rpa sac
                              INNER JOIN bbdd_bigdata_rpa.tb_voz_cliente_n1_crm_allinonegopass_rpa cl1
                                         ON sac.tosac_fk_voz_cliente_n1 = cl1.tvcn1_id
                                             AND cl1.tvcn1_tipo = 'RECUPERADO'
                              INNER JOIN bbdd_bigdata_rpa.tb_voz_cliente_n2_crm_allinonegopass_rpa cl2
                                         ON sac.tosac_fk_voz_cliente_n2 = cl2.tvcn2_id
                                             AND cl2.tvcn2_tipo IN ('RECOBRO POR USUARIO', 'RECARGA')
                              INNER JOIN bbdd_cos_bog_gopass.tb_depurado_go_pass tmp
                                         ON sac.tosac_fk_tipo_dato = tmp.Celular
                     WHERE sac.tosac_fecha BETWEEN @datetime_day AND @datetime_lastday

                     UNION ALL

                     SELECT
                         pg.Celular,
                         pg.FECHA AS fecha_recaudo,
                         'Pago Zeus' AS servicio,
                         CAST(pg.Valor AS DECIMAL(15,2)) AS valor
                     FROM bbdd_cos_bog_gopass.tb_pagos_gopass pg
                              INNER JOIN bbdd_cos_bog_gopass.tb_depurado_go_pass tmp
                                         ON pg.Celular = tmp.Celular
                     WHERE pg.FECHA BETWEEN @date_day AND @last_day
                 ) pagos_consolidados
            GROUP BY celular
        ) pagos ON i.Celular = pagos.celular
    SET i.Fecha_Recaudo = pagos.fecha_recaudo,
        i.Medio_de_Pago = pagos.servicio,
        i.Valor_Recaudado = pagos.valor,
        i.Cant_Recaudos = pagos.cant_recaudo;

#################################### ULTIMA GESTION PREDICTIVO Y BLASTER GOPASS - OPTIMIZADA #######################################
    UPDATE bbdd_cos_bog_gopass.tb_depurado_go_pass i
        INNER JOIN (
            SELECT
                documento,
                call_date,
                phone_number_dialed,
                plataforma,
                tipificacion_vicidial,
                no_contacto
            FROM (
                     SELECT
                         v.address2 AS documento,
                         v.call_date,
                         v.phone_number_dialed,
                         CASE
                             WHEN v.campaign_id = 'GOCOBROS' THEN 'PREDICTIVO'
                             WHEN v.campaign_id = 'BLASTER1' THEN 'BLASTER'
                             ELSE 'Otro'
                             END AS plataforma,
                         COALESCE(tip.status_name, v.status_name) AS tipificacion_vicidial,
                         IF(COALESCE(tip.GESTION, 'CONTACTO') = 'NO CONTACTO', 1, 0) AS no_contacto,
                         ROW_NUMBER() OVER(PARTITION BY v.address2 ORDER BY v.call_date DESC) AS rn
                     FROM bbdd_bigdata_marcaciones_vicidial.tb_marcaciones_vicidial_out_gopass v
                              INNER JOIN bbdd_cos_bog_gopass.tb_depurado_go_pass tmp
                                         ON v.address2 = tmp.doc
                              LEFT JOIN bbdd_cos_bog_gopass.tb_arbol_tipificaciones_vicidial tip
                                        ON v.status = tip.status
                     WHERE v.call_date BETWEEN @datetime_day AND @datetime_lastday
                       AND v.campaign_id IN ('GOCOBROS', 'BLASTER1')
                 ) ranked
            WHERE rn = 1
        ) gestiones ON i.doc = gestiones.documento
    SET i.Fecha_Ultima_Gestion = gestiones.call_date,
        i.Tel_Ultima_Gestion = gestiones.phone_number_dialed,
        i.Planta_telf = gestiones.plataforma,
        i.Estado_Ultima_Gestion = gestiones.tipificacion_vicidial,
        i.No_Contacto = gestiones.no_contacto;

##################### CANTIDAD DE GESTIONES PREDICTIVO GOPASS - OPTIMIZADA ###############################################
    UPDATE bbdd_cos_bog_gopass.tb_depurado_go_pass i
        INNER JOIN (
            SELECT
                address2 AS documento,
                COUNT(*) AS gestiones_vicidial
            FROM bbdd_bigdata_marcaciones_vicidial.tb_marcaciones_vicidial_out_gopass v
                     INNER JOIN bbdd_cos_bog_gopass.tb_depurado_go_pass tmp
                                ON v.address2 = tmp.doc
            WHERE v.call_date BETWEEN @datetime_day AND @datetime_lastday
              AND v.campaign_id = 'GOCOBROS'
            GROUP BY address2
        ) predictivo ON i.doc = predictivo.documento
    SET i.Gestiones_Predictivo = predictivo.gestiones_vicidial;

############# CANTIDAD CONTACTO-NO CONTACTO PREDICTIVO GOPASS - OPTIMIZADA ####################################################
    UPDATE bbdd_cos_bog_gopass.tb_depurado_go_pass i
        INNER JOIN (
            SELECT
                address2 AS documento,
                SUM(CASE WHEN user != 'VDAD' THEN 1 ELSE 0 END) AS total_cto_call_out,
                SUM(CASE WHEN user = 'VDAD' THEN 1 ELSE 0 END) AS total_no_cto_call_out
            FROM bbdd_bigdata_marcaciones_vicidial.tb_marcaciones_vicidial_out_gopass v
                     INNER JOIN bbdd_cos_bog_gopass.tb_depurado_go_pass tmp
                                ON v.address2 = tmp.doc
            WHERE v.call_date BETWEEN @datetime_day AND @datetime_lastday
              AND v.campaign_id = 'GOCOBROS'
            GROUP BY address2
        ) contactos ON i.doc = contactos.documento
    SET i.Total_cto_call_out = contactos.total_cto_call_out,
        i.Total_no_cto_call_out = contactos.total_no_cto_call_out;

##################### CANTIDAD DE GESTIONES BLASTER GOPASS - OPTIMIZADA ###############################################
    UPDATE bbdd_cos_bog_gopass.tb_depurado_go_pass i
        INNER JOIN (
            SELECT
                address2 AS documento,
                COUNT(*) AS gestiones_vicidial
            FROM bbdd_bigdata_marcaciones_vicidial.tb_marcaciones_vicidial_out_gopass v
                     INNER JOIN bbdd_cos_bog_gopass.tb_depurado_go_pass tmp
                                ON v.address2 = tmp.doc
            WHERE v.call_date BETWEEN @datetime_day AND @datetime_lastday
              AND v.campaign_id = 'BLASTER1'
            GROUP BY address2
        ) blaster ON i.doc = blaster.documento
    SET i.Gestiones_Blaster = blaster.gestiones_vicidial;

############################### ACTUALIZA ESTADO GESTION GOPASS #######################
    UPDATE bbdd_cos_bog_gopass.tb_depurado_go_pass
    SET Observacion_Gestion = CASE
                                  WHEN Valor_Recaudado >= 1 THEN 'NO_APLICA_GESTION'
                                  ELSE 'APLICA_GESTION'
        END;

END;
