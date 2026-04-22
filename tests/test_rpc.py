from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

import grpc
import pytest

from generated import phonebook_pb2
from generated import phonebook_pb2_grpc
from phonebook.service import PhonebookService
from phonebook.storage import PhonebookStorage


@pytest.fixture()
def grpc_test_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    storage = PhonebookStorage()
    service = PhonebookService(storage)
    phonebook_pb2_grpc.add_PhonebookServiceServicer_to_server(service, server)

    port = server.add_insecure_port("localhost:0")
    server.start()

    channel = grpc.insecure_channel(f"localhost:{port}")
    grpc.channel_ready_future(channel).result(timeout=5)
    stub = phonebook_pb2_grpc.PhonebookServiceStub(channel)

    yield stub, storage

    channel.close()
    server.stop(0)


def test_rpc_add_lookup_update_delete_and_list(grpc_test_server):
    stub, _ = grpc_test_server

    add_response = stub.AddContact(
        phonebook_pb2.AddContactRequest(name="Alice", phone="12345")
    )
    assert add_response.success is True

    lookup_response = stub.LookupContact(
        phonebook_pb2.LookupContactRequest(name="Alice")
    )
    assert lookup_response.success is True
    assert lookup_response.contact.name == "Alice"
    assert lookup_response.contact.phone == "12345"

    update_response = stub.UpdateContact(
        phonebook_pb2.UpdateContactRequest(name="Alice", new_phone="99999")
    )
    assert update_response.success is True

    list_response = stub.ListContacts(phonebook_pb2.Empty())
    assert len(list_response.contacts) == 1
    assert list_response.contacts[0].name == "Alice"
    assert list_response.contacts[0].phone == "99999"

    delete_response = stub.DeleteContact(
        phonebook_pb2.DeleteContactRequest(name="Alice")
    )
    assert delete_response.success is True

    final_list = stub.ListContacts(phonebook_pb2.Empty())
    assert list(final_list.contacts) == []


def test_rpc_duplicate_add_returns_failure(grpc_test_server):
    stub, _ = grpc_test_server

    first = stub.AddContact(
        phonebook_pb2.AddContactRequest(name="Alice", phone="12345")
    )
    second = stub.AddContact(
        phonebook_pb2.AddContactRequest(name="Alice", phone="00000")
    )

    assert first.success is True
    assert second.success is False
    assert "already exists" in second.message


def test_rpc_concurrent_add_same_contact_only_one_success(grpc_test_server):
    stub, storage = grpc_test_server
    attempts = 25

    def worker(_):
        response = stub.AddContact(
            phonebook_pb2.AddContactRequest(name="Alice", phone="12345")
        )
        return response.success, response.message

    with ThreadPoolExecutor(max_workers=15) as executor:
        results = list(executor.map(worker, range(attempts)))

    success_count = sum(success for success, _ in results)
    failure_count = sum((not success) for success, _ in results)

    assert success_count == 1
    assert failure_count == attempts - 1
    assert storage.list_contacts() == {"Alice": "12345"}


def test_rpc_concurrent_add_different_contacts(grpc_test_server):
    stub, storage = grpc_test_server
    total_contacts = 40

    def worker(i: int):
        return stub.AddContact(
            phonebook_pb2.AddContactRequest(name=f"User{i}", phone=f"7000{i}")
        )

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(worker, range(total_contacts)))

    assert all(response.success for response in results)
    contacts = storage.list_contacts()
    assert len(contacts) == total_contacts

    for i in range(total_contacts):
        assert contacts[f"User{i}"] == f"7000{i}"


def test_rpc_concurrent_lookup_returns_consistent_values(grpc_test_server):
    stub, _ = grpc_test_server
    stub.AddContact(phonebook_pb2.AddContactRequest(name="Bob", phone="55555"))

    def worker(_):
        response = stub.LookupContact(phonebook_pb2.LookupContactRequest(name="Bob"))
        return response.success, response.contact.phone

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(worker, range(60)))

    assert all(success for success, _ in results)
    assert all(phone == "55555" for _, phone in results)
