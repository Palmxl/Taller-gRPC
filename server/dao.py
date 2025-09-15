import sqlite3, os
from contextlib import contextmanager

# ubicación base del proyecto (carpeta actual del archivo)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# clase que representa un libro en memoria
class Book:
    def __init__(self, isbn, title, total, loaned):
        self.isbn = isbn
        self.title = title
        self.copies_total = total
        self.copies_loaned = loaned

# clase que maneja todas las operaciones sobre la base de datos
class BookDao:
    def __init__(self, db_path="library.db"):
        # si la ruta no es absoluta, se une con la carpeta base
        if not os.path.isabs(db_path):
            db_path = os.path.join(BASE_DIR, db_path)
        self.db_path = db_path

    # contexto para abrir y cerrar la conexión automáticamente
    @contextmanager
    def conn(self):
        con = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            yield con
        finally:
            con.close()

    # crea la tabla de libros si no existe
    def ensure_schema(self):
        with self.conn() as c:
            c.execute("""
            CREATE TABLE IF NOT EXISTS books(
              isbn TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              copies_total INTEGER NOT NULL,
              copies_loaned INTEGER NOT NULL DEFAULT 0
            );
            """)
            c.commit()

    # agrega algunos registros de ejemplo si no están en la base
    def seed(self):
        with self.conn() as c:
            c.executemany(
              "INSERT OR IGNORE INTO books(isbn,title,copies_total,copies_loaned) VALUES (?,?,?,?)",
              [
                ("9780134685991", "Effective Java", 3, 0),
                ("9781491950357", "Designing Data-Intensive Applications", 2, 0),
                ("9780132350884", "Clean Code", 4, 0),
              ]
            )
            c.commit()

    # busca un libro por ISBN
    def get_by_isbn(self, isbn):
        with self.conn() as c:
            cur = c.execute("SELECT isbn,title,copies_total,copies_loaned FROM books WHERE isbn=?", (isbn,))
            row = cur.fetchone()
            return Book(*row) if row else None

    # busca el primer libro que coincida con el título
    def get_first_by_title(self, title):
        with self.conn() as c:
            cur = c.execute(
                "SELECT isbn,title,copies_total,copies_loaned FROM books WHERE title LIKE ? LIMIT 1",
                (f"%{title}%",)
            )
            row = cur.fetchone()
            return Book(*row) if row else None

    # incrementa la cantidad de préstamos de un libro (solo si hay copias disponibles)
    def increment_loan(self, isbn):
        with self.conn() as c:
            cur = c.execute(
                "UPDATE books SET copies_loaned = copies_loaned + 1 WHERE isbn=? AND copies_loaned < copies_total",
                (isbn,)
            )
            if cur.rowcount == 0:
                raise RuntimeError("Sin copias disponibles")
            c.commit()

    # disminuye la cantidad de préstamos de un libro (solo si había préstamos activos)
    def decrement_loan(self, isbn):
        with self.conn() as c:
            cur = c.execute(
                "UPDATE books SET copies_loaned = copies_loaned - 1 WHERE isbn=? AND copies_loaned > 0",
                (isbn,)
            )
            if cur.rowcount == 0:
                raise RuntimeError("No había préstamo activo")
            c.commit()