import os
from .dao import BookDao, BASE_DIR

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(base_dir, "library.db")
    dao = BookDao(db_file)
    dao.ensure_schema()
    dao.seed()
    print("BD inicializada en:", db_file)