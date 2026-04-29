from phonebook.signing import (
    canonical_contact,
    canonical_contacts,
    sign_payload,
    verify_signature,
)


def test_sign_and_verify_payload():
    payload = "Alice:12345"

    signature = sign_payload(payload)

    assert signature
    assert verify_signature(payload, signature) is True


def test_verification_fails_for_tampered_payload():
    original_payload = "Alice:12345"
    tampered_payload = "Alice:99999"

    signature = sign_payload(original_payload)

    assert verify_signature(tampered_payload, signature) is False


def test_canonical_contact_format():
    assert canonical_contact("Alice", "12345") == "Alice:12345"


def test_canonical_contacts_are_sorted():
    contacts = {
        "Charlie": "33333",
        "Alice": "11111",
        "Bob": "22222",
    }

    assert canonical_contacts(contacts) == "Alice:11111|Bob:22222|Charlie:33333"


def test_empty_contacts_payload_is_empty_string():
    assert canonical_contacts({}) == ""
