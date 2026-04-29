from concurrent import futures

import grpc

from generated import phonebook_pb2_grpc
from phonebook.service import PhonebookService
from phonebook.storage import PhonebookStorage


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    storage = PhonebookStorage()
    service = PhonebookService(storage)

    phonebook_pb2_grpc.add_PhonebookServiceServicer_to_server(
        service,
        server
    )

    server.add_insecure_port("[::]:50051")

    print("Write-once phonebook server started on port 50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
