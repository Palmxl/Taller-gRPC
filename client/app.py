import grpc
from lib import library_pb2, library_pb2_grpc

def main():
    # conexión al servidor gRPC usando ip y puerto definidos
    channel = grpc.insecure_channel("10.43.103.200:8080")
    # creación del stub para poder invocar los métodos del servicio remoto
    stub = library_pb2_grpc.LibraryServiceStub(channel)

    while True:
        # menú de opciones para el usuario
        print("\n1) Consulta ISBN  2) Prestamo ISBN  3) Prestamo Titulo  4) Devolucion ISBN  0) Salir") 
        op = input("> ").strip()
        try:
            if op == "1":
                # consulta de libro por ISBN, devuelve si existe, cuántos hay y el título
                isbn = input("ISBN: ")
                r = stub.QueryByIsbn(library_pb2.QueryByIsbnRequest(isbn=isbn))
                print(f"Existe: {r.exists}, Disponibles: {r.copies_available}, Título: {r.title}")
            elif op == "2":
                # préstamo de libro usando ISBN, devuelve mensaje y fecha de devolución
                isbn = input("ISBN: ")
                r = stub.LoanByIsbn(library_pb2.LoanByIsbnRequest(isbn=isbn, user_id="demo"))
                print(f"{r.message} | Devuelve el: {r.due_date_iso}")
            elif op == "3":
                # préstamo de libro buscando por título
                title = input("Título: ")
                r = stub.LoanByTitle(library_pb2.LoanByTitleRequest(title=title, user_id="demo"))
                print(f"{r.message} | Devuelve el: {r.due_date_iso}")
            elif op == "4":
                # devolución de libro por ISBN
                isbn = input("ISBN: ")
                r = stub.ReturnByIsbn(library_pb2.ReturnRequest(isbn=isbn, user_id="demo"))
                print(r.message)
            elif op == "0":
                # salir del programa
                break
            else:
                # opción no válida
                print("Opción inválida")
        except grpc.RpcError as e:
            # manejo de error en caso de fallo en la llamada gRPC
            print(f"Error: {e.code().name} - {e.details()}")

if __name__ == "__main__":
    main()