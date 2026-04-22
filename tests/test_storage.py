import pytest

from phonebook.storage import PhonebookStorage


def test_add_lookup_update_delete_and_list_contact():
    storage = PhonebookStorage()

    message = storage.add_contact("Alice", "12345")
    assert message == "Contact 'Alice' added"

    assert storage.lookup_contact("Alice") == "12345"

    message = storage.update_contact("Alice", "99999")
    assert message == "Contact 'Alice' updated"
    assert storage.lookup_contact("Alice") == "99999"

    contacts = storage.list_contacts()
    assert contacts == {"Alice": "99999"}

    message = storage.delete_contact("Alice")
    assert message == "Contact 'Alice' deleted"
    assert storage.list_contacts() == {}


def test_add_duplicate_contact_raises_value_error():
    storage = PhonebookStorage()
    storage.add_contact("Alice", "12345")

    with pytest.raises(ValueError, match="already exists"):
        storage.add_contact("Alice", "00000")


def test_lookup_missing_contact_raises_key_error():
    storage = PhonebookStorage()

    with pytest.raises(KeyError, match="not found"):
        storage.lookup_contact("Missing")


def test_update_missing_contact_raises_key_error():
    storage = PhonebookStorage()

    with pytest.raises(KeyError, match="not found"):
        storage.update_contact("Missing", "11111")


def test_delete_missing_contact_raises_key_error():
    storage = PhonebookStorage()

    with pytest.raises(KeyError, match="not found"):
        storage.delete_contact("Missing")


def test_add_empty_name_raises_value_error():
    storage = PhonebookStorage()

    with pytest.raises(ValueError, match="Name cannot be empty"):
        storage.add_contact("   ", "12345")


def test_add_empty_phone_raises_value_error():
    storage = PhonebookStorage()

    with pytest.raises(ValueError, match="Phone cannot be empty"):
        storage.add_contact("Alice", "   ")


def test_update_empty_phone_raises_value_error():
    storage = PhonebookStorage()
    storage.add_contact("Alice", "12345")

    with pytest.raises(ValueError, match="Phone cannot be empty"):
        storage.update_contact("Alice", "   ")


def test_lookup_empty_name_raises_value_error():
    storage = PhonebookStorage()

    with pytest.raises(ValueError, match="Name cannot be empty"):
        storage.lookup_contact("   ")
