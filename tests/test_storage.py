import pytest

from phonebook.storage import PhonebookStorage


def test_add_lookup_and_list_contact():
    storage = PhonebookStorage()

    message = storage.add_contact("Alice", "12345")
    assert message == "Contact 'Alice' added"

    assert storage.lookup_contact("Alice") == "12345"

    contacts = storage.list_contacts()
    assert contacts == {"Alice": "12345"}


def test_write_once_duplicate_contact_raises_value_error():
    storage = PhonebookStorage()

    storage.add_contact("Alice", "12345")

    with pytest.raises(ValueError, match="write-once phonebook does not allow overwrites"):
        storage.add_contact("Alice", "99999")

    assert storage.lookup_contact("Alice") == "12345"
    assert storage.list_contacts() == {"Alice": "12345"}


def test_lookup_missing_contact_raises_key_error():
    storage = PhonebookStorage()

    with pytest.raises(KeyError, match="not found"):
        storage.lookup_contact("Missing")


def test_add_empty_name_raises_value_error():
    storage = PhonebookStorage()

    with pytest.raises(ValueError, match="Name cannot be empty"):
        storage.add_contact("   ", "12345")


def test_add_empty_phone_raises_value_error():
    storage = PhonebookStorage()

    with pytest.raises(ValueError, match="Phone cannot be empty"):
        storage.add_contact("Alice", "   ")


def test_lookup_empty_name_raises_value_error():
    storage = PhonebookStorage()

    with pytest.raises(ValueError, match="Name cannot be empty"):
        storage.lookup_contact("   ")


def test_list_contacts_returns_copy_not_internal_dictionary():
    storage = PhonebookStorage()
    storage.add_contact("Alice", "12345")

    contacts = storage.list_contacts()
    contacts["Mallory"] = "00000"

    assert storage.list_contacts() == {"Alice": "12345"}
