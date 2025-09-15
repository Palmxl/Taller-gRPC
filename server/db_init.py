import os
from .dao import BookDao, BASE_DIR

if __name__ == "__main__":
    # ruta de la carpeta actual
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # ruta completa al archivo de la base de datos
    db_file = os.path.join(base_dir, "library.db")
    # creación del objeto DAO para manejar la BD
    dao = BookDao(db_file)
    # asegura que la tabla de libros exista
    dao.ensure_schema()
    # inserta algunos registros de ejemplo
    dao.seed()
    # mensaje de confirmación
    print("BD inicializada en:", db_file)