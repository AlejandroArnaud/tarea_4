# main_etl.py
import configparser
import db_utils
import etl_processor

def display_menu():
    """Muestra un menú interactivo y devuelve la opción del usuario."""
    print("\n===== MENÚ DE CONFIGURACIÓN DEL ETL =====")
    print("Por favor, elija el destino de la base de datos:")
    print("1. MySQL")
    print("2. SQLite")
    choice = input("Ingrese su opción (1 o 2): ")
    while choice not in ['1', '2']:
        choice = input("Opción inválida. Por favor, ingrese 1 o 2: ")
    return 'mysql' if choice == '1' else 'sqlite'

def main():
    """Función principal que orquesta el pipeline ETL."""
    try:
        # Leer el archivo de configuración
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        if not config.sections():
            print("Error: No se pudo leer el archivo 'config.ini' o está vacío.")
            return

        # Mostrar menú y obtener la elección del usuario
        db_type = display_menu()
        
        # Crear el motor de la base de datos
        engine = db_utils.create_db_engine(config, db_type)

        if engine:
            print("Conexión a la base de datos establecida exitosamente.")
            # Ejecutar el proceso ETL completo
            etl_processor.run_full_etl(engine, config)
            print("\n¡Proceso ETL finalizado!")
        else:
            print("No se pudo establecer la conexión a la base de datos. Abortando.")

    except Exception as e:
        print(f"Ha ocurrido un error inesperado en el proceso principal: {e}")

if __name__ == "__main__":
    main()