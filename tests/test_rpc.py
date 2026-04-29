from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

import grpc
import pytest

from generated import phonebook_pb2
from generated import phonebook_pb2_grpc
from phonebook.service import PhonebookService
from phonebook.signing import canonical_contact, canonical_contacts, verify_signature
from phonebook.storage import PhonebookStorage


@pytest.fixture()
def grpc_test_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    storage = PhonebookStorage()
    service = PhonebookService(storage)

    phonebook_pb2_grpc.add_PhonebookServiceServicer_to_server(
        service,
        server
    )

    port = server.add_insecure_port("localhost:0")
    server.start()

    channel = grpc.insecure_channel(f"localhost:{port}")
    grpc.channel_ready_future(channel).result(timeout=5)

    stub = phonebook_pb2_grpc.PhonebookServiceStub(channel)

    yield stub, storage

    channel.close()
    server.stop(0)


def test_rpc_add_lookup_and_list_with_valid_signatures(grpc_test_server):
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

    lookup_payload = canonical_contact(
        lookup_response.contact.name,
        lookup_response.contact.phone
    )

    assert verify_signature(lookup_payload, lookup_response.signature) is True

    list_response = stub.ListContacts(phonebook_pb2.Empty())

    contacts = {
        contact.name: contact.phone
        for contact in list_response.contacts
    }

    list_payload = canonical_contacts(contacts)

    assert contacts == {"Alice": "12345"}
    assert verify_signature(list_payload, list_response.signature) is True


def test_rpc_duplicate_add_returns_failure_and_does_not_overwrite(grpc_test_server):
    stub, storage = grpc_test_server

    first = stub.AddContact(
        phonebook_pb2.AddContactRequest(name="Alice", phone="12345")
    )

    second = stub.AddContact(
        phonebook_pb2.AddContactRequest(name="Alice", phone="99999")
    )

    assert first.success is True
    assert second.success is False
    assert "write-once phonebook does not allow overwrites" in second.message

    assert storage.list_contacts() == {"Alice": "12345"}


def test_rpc_lookup_missing_contact_returns_failure(grpc_test_server):
    stub, _ = grpc_test_server

    response = stub.LookupContact(
        phonebook_pb2.LookupContactRequest(name="Missing")
    )

    assert response.success is False
    assert "not found" in response.message
    assert response.signature == ""


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


def test_rpc_concurrent_lookup_returns_consistent_signed_values(grpc_test_server):
    stub, _ = grpc_test_server

    stub.AddContact(
        phonebook_pb2.AddContactRequest(name="Bob", phone="55555")
    )

    def worker(_):
        response = stub.LookupContact(
            phonebook_pb2.LookupContactRequest(name="Bob")
        )

        payload = canonical_contact(
            response.contact.name,
            response.contact.phone
        )

        return response.success, response.contact.phone, verify_signature(payload, response.signature)

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(worker, range(60)))

    assert all(success for success, _, _ in results)
    assert all(phone == "55555" for _, phone, _ in results)
    assert all(signature_valid for _, _, signature_valid in results)


def test_rpc_signature_fails_if_payload_is_tampered(grpc_test_server):
    stub, _ = grpc_test_server

    stub.AddContact(
        phonebook_pb2.AddContactRequest(name="Alice", phone="12345")
    )

    response = stub.LookupContact(
        phonebook_pb2.LookupContactRequest(name="Alice")
    )

    tampered_payload = canonical_contact("Alice", "99999")

    assert verify_signature(tampered_payload, response.signature) is False
