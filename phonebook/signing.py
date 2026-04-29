import hashlib
import hmac

SECRET_KEY = b"phonebook-server-secret-key"


def sign_payload(payload: str) -> str:
    return hmac.new(
        SECRET_KEY,
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def verify_signature(payload: str, signature: str) -> bool:
    expected_signature = sign_payload(payload)
    return hmac.compare_digest(expected_signature, signature)


def canonical_contact(name: str, phone: str) -> str:
    return f"{name}:{phone}"


def canonical_contacts(contacts: dict) -> str:
    return "|".join(
        f"{name}:{phone}"
        for name, phone in sorted(contacts.items())
    )
