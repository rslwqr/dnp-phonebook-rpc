import grpc

from generated import phonebook_pb2
from generated import phonebook_pb2_grpc
from phonebook.signing import canonical_contact, canonical_contacts, verify_signature


HOST = "localhost"
PORT = 50051


def print_menu():
    print("\nWrite-once Phonebook Client Menu:")
    print("1. Add contact")
    print("2. Lookup contact")
    print("3. List contacts")
    print("4. Exit")


def add_contact(stub):
    name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()

    response = stub.AddContact(
        phonebook_pb2.AddContactRequest(name=name, phone=phone)
    )

    print(response.message)


def lookup_contact(stub):
    name = input("Enter name to lookup: ").strip()

    response = stub.LookupContact(
        phonebook_pb2.LookupContactRequest(name=name)
    )

    if not response.success:
        print(response.message)
        return

    payload = canonical_contact(response.contact.name, response.contact.phone)
    is_valid = verify_signature(payload, response.signature)

    print(f"Name: {response.contact.name}, Phone: {response.contact.phone}")
    print(f"Signature: {response.signature}")
    print(f"Signature valid: {is_valid}")


def list_contacts(stub):
    response = stub.ListContacts(phonebook_pb2.Empty())

    if not response.contacts:
        payload = canonical_contacts({})
        is_valid = verify_signature(payload, response.signature)

        print("Phonebook is empty")
        print(f"Signature: {response.signature}")
        print(f"Signature valid: {is_valid}")
        return

    contacts = {
        contact.name: contact.phone
        for contact in response.contacts
    }

    payload = canonical_contacts(contacts)
    is_valid = verify_signature(payload, response.signature)

    print("\nContacts:")
    for contact in response.contacts:
        print(f"- {contact.name}: {contact.phone}")

    print(f"Signature: {response.signature}")
    print(f"Signature valid: {is_valid}")


def run_client():
    with grpc.insecure_channel(f"{HOST}:{PORT}") as channel:
        stub = phonebook_pb2_grpc.PhonebookServiceStub(channel)

        while True:
            print_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                add_contact(stub)
            elif choice == "2":
                lookup_contact(stub)
            elif choice == "3":
                list_contacts(stub)
            elif choice == "4":
                print("Exiting client")
                break
            else:
                print("Invalid option, please try again.")


if __name__ == "__main__":
    run_client()
