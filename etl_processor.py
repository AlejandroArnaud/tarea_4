import pandas as pd
from sqlalchemy.engine import Engine
from tqdm import tqdm
import os
import db_utils

# --- FUNCIONES DE TRANSFORMACIÓN ESPECÍFICAS ---


def transform_assessments(df: pd.DataFrame, courses_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma el dataframe de 'assessments' aplicando reglas de negocio.
    Regla: Si es un examen ('Exam') y la fecha es nula, se imputa con la
           duración del curso correspondiente.
    """
    # Unir con los datos de cursos para obtener la duración (length)
    df_merged = pd.merge(
        df, courses_df, on=["code_module", "code_presentation"], how="left"
    )

    # Condición para la imputación de fechas de examen
    condition = (df_merged["assessment_type"] == "Exam") & (df_merged["date"].isnull())

    # Aplicar la regla de negocio
    df_merged.loc[condition, "date"] = df_merged.loc[
        condition, "module_presentation_length"
    ]

    # Asegurar que las columnas del dataframe original se mantengan
    return df_merged[df.columns]


def transform_student_assessment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma el dataframe de 'studentAssessment' aplicando reglas de negocio.
    Regla: Crea el campo de dominio 'assessment_result' basado en el 'score'.
           Un score menor a 40 es 'Fail', de lo contrario es 'Pass'.
    """

    def classify_score(score):
        if pd.isna(score):
            return None
        return "Pass" if float(score) >= 40 else "Fail"

    df["assessment_result"] = df["score"].apply(classify_score)
    return df


def transform_generic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función de transformación por defecto para tablas que no necesitan
    lógica de negocio específica.
    """
    return df


# --- PROCESADOR PRINCIPAL DEL ETL ---


def process_csv_to_db(
    filepath: str,
    table_name: str,
    engine: Engine,
    batch_size: int,
    transform_func,
    **kwargs,
):
    """
    Procesa un archivo CSV en lotes, lo transforma y lo carga en la base de datos,
    controlando el progreso para poder reanudar el proceso si falla.
    """
    print(f"\n--- Iniciando procesamiento para la tabla: {table_name} ---")

    if not os.path.exists(filepath):
        print(f"Error: El archivo no fue encontrado en la ruta '{filepath}'")
        return

    start_chunk = db_utils.get_last_processed_chunk(table_name, engine)

    try:
        # Se define una lista de valores a ser tratados como nulos.
        # Esto maneja tanto '?' como cadenas vacías ''.
        missing_values = ["?", ""]

        # El procesamiento se realiza en un `with` para asegurar que el lector de archivos se cierre.
        with pd.read_csv(
            filepath, chunksize=batch_size, iterator=True, na_values=missing_values
        ) as reader:
            for i, chunk in enumerate(
                tqdm(reader, desc=f"Cargando {table_name}", unit=" chunks")
            ):
                current_chunk_index = i + 1

                if current_chunk_index <= start_chunk:
                    continue

                # NOTA: La limpieza de '?' y '' ya no es necesaria aquí,
                # pd.read_csv con na_values lo maneja eficientemente en la lectura.

                # 1. Aplicar función de transformación específica de la tabla
                transformed_chunk = transform_func(chunk, **kwargs)

                # 2. Carga (Load) y actualización del log dentro de una transacción atómica
                with engine.begin() as connection:
                    transformed_chunk.to_sql(
                        table_name, con=connection, if_exists="append", index=False
                    )
                    db_utils.update_etl_log(table_name, current_chunk_index, connection)

        print(f"Procesamiento de '{table_name}' completado exitosamente.")

    except Exception as e:
        print(f"\nError durante el procesamiento de '{table_name}': {e}")
        print(
            "El proceso se ha detenido. Puede reanudarlo ejecutando el script nuevamente."
        )


def run_full_etl(engine: Engine, config):
    """
    Orquesta el proceso ETL completo, cargando todas las tablas en el orden correcto
    y aplicando las transformaciones de negocio necesarias.
    """
    batch_size = int(config["etl_settings"]["batch_size"])
    data_path = config["etl_settings"]["data_path"]

    db_utils.setup_etl_log_table(engine)

    # Precargar datos de cursos en memoria, ya que son necesarios para la transformación de 'assessments'
    try:
        courses_filepath = os.path.join(data_path, "courses.csv")
        courses_df = pd.read_csv(courses_filepath)
        print("Datos de 'courses' precargados para asistir en transformaciones.")
    except FileNotFoundError:
        print(
            f"Error fatal: {courses_filepath} no encontrado. Es un archivo esencial para el ETL. Abortando."
        )
        return

    # Plan de ejecución del ETL, mapeando tablas a sus funciones de transformación y dependencias
    etl_plan = {
        "courses": {"func": transform_generic, "args": {}},
        "vle": {"func": transform_generic, "args": {}},
        "studentInfo": {"func": transform_generic, "args": {}},
        "studentRegistration": {"func": transform_generic, "args": {}},
        "assessments": {
            "func": transform_assessments,
            "args": {"courses_df": courses_df},
        },
        "studentAssessment": {"func": transform_student_assessment, "args": {}},
        "studentVle": {"func": transform_generic, "args": {}},
    }

    # Orden de ejecución para respetar las restricciones de llaves foráneas
    execution_order = [
        "courses",
        "vle",
        "studentInfo",
        "studentRegistration",
        "assessments",
        "studentAssessment",
        "studentVle",
    ]

    for table_name in execution_order:
        plan = etl_plan[table_name]
        filename = f"{table_name}.csv"
        filepath = os.path.join(data_path, filename)

        process_csv_to_db(
            filepath, table_name, engine, batch_size, plan["func"], **plan["args"]
        )
