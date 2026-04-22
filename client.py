import grpc

from generated import phonebook_pb2
from generated import phonebook_pb2_grpc


HOST = "localhost"
PORT = 50051


def print_menu():
    print("\nPhonebook Client Menu:")
    print("1. Add contact")
    print("2. Lookup contact")
    print("3. Update contact")
    print("4. Delete contact")
    print("5. List contacts")
    print("6. Exit")


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

    if response.success:
        print(f"Name: {response.contact.name}, Phone: {response.contact.phone}")
    else:
        print(response.message)


def update_contact(stub):
    name = input("Enter name to update: ").strip()
    new_phone = input("Enter new phone: ").strip()

    response = stub.UpdateContact(
        phonebook_pb2.UpdateContactRequest(name=name, new_phone=new_phone)
    )

    print(response.message)


def delete_contact(stub):
    name = input("Enter name to delete: ").strip()

    response = stub.DeleteContact(
        phonebook_pb2.DeleteContactRequest(name=name)
    )

    print(response.message)


def list_contacts(stub):
    response = stub.ListContacts(phonebook_pb2.Empty())

    if not response.contacts:
        print("Phonebook is empty")
        return

    print("\nContacts:")
    for contact in response.contacts:
        print(f"- {contact.name}: {contact.phone}")


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
                update_contact(stub)
            elif choice == "4":
                delete_contact(stub)
            elif choice == "5":
                list_contacts(stub)
            elif choice == "6":
                print("Exiting client")
                break
            else:
                print("Invalid option, please try again.")


if __name__ == "__main__":
    run_client()