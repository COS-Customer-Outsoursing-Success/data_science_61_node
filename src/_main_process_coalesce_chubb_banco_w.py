from coalesce._cls_etl_coalesce_ import EtlCoalesceTel

def main():

    schema = 'bbdd_cos_bog_chubb'

    table = 'tb_asignacion_banco_w_v2_coalesce'
    
    cuenta = 'numero_id'

    sql_file_path = r'C:\Users\Emerson.Aguilar\Documents\git_hub\Chubb\sql\_sql_coalesce_chubb_banco_w.sql'
    
    phone_columns = [
                'celular_personal', 
                    'celular_negocio',
                    'telefono_domicilio',
                    'repoblacion_repo1',
                    'repoblacion_repo2',
                    'repoblacion_repo3',
                    'repoblacion_repo5',
                    'repoblacion_repo6'
    ]
    processor = EtlCoalesceTel(
        schema=schema,
        table=table,
        sql_file_path=sql_file_path,
        cuenta=cuenta,
        phone_columns=phone_columns
    )

    try:
#        processor.clean_table()
        processor.coalesce_etl()
        processor.load_data()
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")

if __name__ == '__main__':
    main()
