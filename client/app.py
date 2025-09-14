import grpc
from lib import library_pb2, library_pb2_grpc

def main():
    channel = grpc.insecure_channel("10.43.103.200:8080")
    stub = library_pb2_grpc.LibraryServiceStub(channel)

    while True:
        print("\n1) QueryByIsbn  2) LoanByIsbn  3) LoanByTitle  4) ReturnByIsbn  0) Salir")
        op = input("> ").strip()
        try:
            if op == "1":
                isbn = input("ISBN: ")
                r = stub.QueryByIsbn(library_pb2.QueryByIsbnRequest(isbn=isbn))
                print(f"Existe: {r.exists}, Disponibles: {r.copies_available}, Título: {r.title}")
            elif op == "2":
                isbn = input("ISBN: ")
                r = stub.LoanByIsbn(library_pb2.LoanByIsbnRequest(isbn=isbn, user_id="demo"))
                print(f"{r.message} | Devuelve el: {r.due_date_iso}")
            elif op == "3":
                title = input("Título: ")
                r = stub.LoanByTitle(library_pb2.LoanByTitleRequest(title=title, user_id="demo"))
                print(f"{r.message} | Devuelve el: {r.due_date_iso}")
            elif op == "4":
                isbn = input("ISBN: ")
                r = stub.ReturnByIsbn(library_pb2.ReturnRequest(isbn=isbn, user_id="demo"))
                print(r.message)
            elif op == "0":
                break
            else:
                print("Opción inválida")
        except grpc.RpcError as e:
            print(f"Error: {e.code().name} - {e.details()}")

if __name__ == "__main__":
    main()