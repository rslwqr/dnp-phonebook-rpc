import threading


class PhonebookStorage:

    def __init__(self):
        self._contacts = {}
        self._lock = threading.Lock()

    def add_contact(self, name: str, phone: str) -> str:
        name = name.strip()
        phone = phone.strip()

        if not name:
            raise ValueError("Name cannot be empty")
        if not phone:
            raise ValueError("Phone cannot be empty")

        with self._lock:
            if name in self._contacts:
                raise ValueError(
                    f"Contact '{name}' already exists; write-once phonebook does not allow overwrites"
                )

            self._contacts[name] = phone

        return f"Contact '{name}' added"

    def lookup_contact(self, name: str) -> str:
        name = name.strip()

        if not name:
            raise ValueError("Name cannot be empty")

        with self._lock:
            if name not in self._contacts:
                raise KeyError(f"Contact '{name}' not found")

            return self._contacts[name]

    def list_contacts(self) -> dict:
        with self._lock:
            return dict(self._contacts)
