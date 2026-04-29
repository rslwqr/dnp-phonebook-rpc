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
        except ValueError as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(worker, range(attempts)))

    assert results.count("success") == 1
    assert sum("write-once phonebook does not allow overwrites" in result for result in results) == attempts - 1

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


def test_concurrent_duplicate_add_does_not_overwrite_original_value():
    storage = PhonebookStorage()
    storage.add_contact("Alice", "11111")

    new_numbers = [f"9{i:04d}" for i in range(40)]

    def worker(number: str):
        try:
            storage.add_contact("Alice", number)
            return "success"
        except ValueError as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(worker, new_numbers))

    assert "success" not in results
    assert all("write-once phonebook does not allow overwrites" in result for result in results)

    assert storage.lookup_contact("Alice") == "11111"
    assert storage.list_contacts() == {"Alice": "11111"}


def test_concurrent_mixed_add_and_lookup_keeps_consistent_state():
    storage = PhonebookStorage()

    def add_worker(i: int):
        return storage.add_contact(f"User{i}", f"7000{i}")

    def lookup_worker(i: int):
        try:
            return storage.lookup_contact(f"User{i}")
        except KeyError as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=30) as executor:
        add_futures = [executor.submit(add_worker, i) for i in range(30)]
        lookup_futures = [executor.submit(lookup_worker, i) for i in range(30)]

        add_results = [future.result() for future in add_futures]
        lookup_results = [future.result() for future in lookup_futures]

    assert len(add_results) == 30
    assert len(storage.list_contacts()) == 30

    for result in lookup_results:
        assert result.startswith("7000") or "not found" in result
