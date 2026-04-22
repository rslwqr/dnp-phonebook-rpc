from concurrent.futures import ThreadPoolExecutor

from phonebook.storage import PhonebookStorage


def test_concurrent_add_different_contacts():
    storage = PhonebookStorage()
    total_contacts = 50

    def worker(i: int):
        return storage.add_contact(f"User{i}", f"1000{i}")

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(worker, range(total_contacts)))

    assert len(results) == total_contacts
    contacts = storage.list_contacts()
    assert len(contacts) == total_contacts

    for i in range(total_contacts):
        assert contacts[f"User{i}"] == f"1000{i}"


def test_concurrent_add_same_contact_only_one_success():
    storage = PhonebookStorage()
    attempts = 30

    def worker(_):
        try:
            storage.add_contact("Alice", "12345")
            return "success"
        except ValueError as exc:
            return str(exc)

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(worker, range(attempts)))

    assert results.count("success") == 1
    assert sum("already exists" in result for result in results) == attempts - 1
    assert storage.lookup_contact("Alice") == "12345"
    assert storage.list_contacts() == {"Alice": "12345"}


def test_concurrent_lookup_returns_consistent_values():
    storage = PhonebookStorage()
    storage.add_contact("Alice", "12345")

    def worker(_):
        return storage.lookup_contact("Alice")

    with ThreadPoolExecutor(max_workers=25) as executor:
        results = list(executor.map(worker, range(100)))

    assert all(result == "12345" for result in results)


def test_concurrent_update_same_contact_keeps_consistent_state():
    storage = PhonebookStorage()
    storage.add_contact("Alice", "00000")
    new_numbers = [f"9{i:04d}" for i in range(40)]

    def worker(number: str):
        return storage.update_contact("Alice", number)

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(worker, new_numbers))

    assert len(results) == len(new_numbers)
    final_phone = storage.lookup_contact("Alice")
    assert final_phone in new_numbers
    assert storage.list_contacts() == {"Alice": final_phone}


def test_concurrent_delete_and_lookup_do_not_corrupt_state():
    storage = PhonebookStorage()
    storage.add_contact("Bob", "55555")

    def delete_worker():
        try:
            storage.delete_contact("Bob")
            return "deleted"
        except KeyError as exc:
            return str(exc)

    def lookup_worker():
        try:
            return storage.lookup_contact("Bob")
        except KeyError as exc:
            return str(exc)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(lookup_worker) for _ in range(20)]
        futures.append(executor.submit(delete_worker))
        results = [future.result() for future in futures]

    assert any(result == "deleted" for result in results)
    assert storage.list_contacts() == {}

    for result in results:
        assert result == "55555" or result == "deleted" or "not found" in result
