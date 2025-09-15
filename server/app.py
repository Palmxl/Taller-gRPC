from concurrent import futures
import grpc
from datetime import date, timedelta

from .dao import BookDao, BASE_DIR
from lib import library_pb2, library_pb2_grpc

# implementación del servicio definido en library.proto
class LibraryService(library_pb2_grpc.LibraryServiceServicer):
    def __init__(self, dao: BookDao):
        self.dao = dao  # acceso a la base de datos de libros

    # préstamo de libro por ISBN
    def LoanByIsbn(self, request, context):
        book = self.dao.get_by_isbn(request.isbn)
        if not book:
            context.abort(grpc.StatusCode.NOT_FOUND, "Libro no encontrado")
        if book.copies_loaned >= book.copies_total:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Sin copias disponibles")
        self.dao.increment_loan(request.isbn)
        due = (date.today() + timedelta(days=7)).isoformat()
        return library_pb2.LoanResponse(ok=True, message="Préstamo aprobado", due_date_iso=due)

    # préstamo de libro por título
    def LoanByTitle(self, request, context):
        book = self.dao.get_first_by_title(request.title)
        if not book:
            context.abort(grpc.StatusCode.NOT_FOUND, "Título no encontrado")
        if book.copies_loaned >= book.copies_total:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Sin copias disponibles")
        self.dao.increment_loan(book.isbn)
        due = (date.today() + timedelta(days=7)).isoformat()
        return library_pb2.LoanResponse(ok=True, message="Préstamo aprobado", due_date_iso=due)

    # consulta de disponibilidad por ISBN
    def QueryByIsbn(self, request, context):
        book = self.dao.get_by_isbn(request.isbn)
        if not book:
            return library_pb2.QueryResponse(exists=False)
        available = book.copies_total - book.copies_loaned
        return library_pb2.QueryResponse(exists=True, copies_available=available, title=book.title)

    # devolución de libro por ISBN
    def ReturnByIsbn(self, request, context):
        book = self.dao.get_by_isbn(request.isbn)
        if not book:
            context.abort(grpc.StatusCode.NOT_FOUND, "ISBN no encontrado")
        if book.copies_loaned <= 0:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "No hay préstamos activos")
        self.dao.decrement_loan(request.isbn)
        return library_pb2.ReturnResponse(ok=True, message="Devolución registrada")

# arranque del servidor gRPC
def serve():
    dao = BookDao("library.db")        # inicializa base de datos
    dao.ensure_schema()                # crea tablas si no existen
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    library_pb2_grpc.add_LibraryServiceServicer_to_server(LibraryService(dao), server)
    server.add_insecure_port("0.0.0.0:8080")  # escucha en todas las interfaces, puerto 8080
    server.start()
    print("Servidor gRPC en puerto 8080")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()