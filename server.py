import grpc
from concurrent import futures

from generated import phonebook_pb2_grpc

from phonebook.storage import PhonebookStorage
from phonebook.service import PhonebookService


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    storage = PhonebookStorage()
    service = PhonebookService(storage)


    phonebook_pb2_grpc.add_PhonebookServiceServicer_to_server(
        service, server
    )


    server.add_insecure_port("[::]:50051")

    print("Server started on port 50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()