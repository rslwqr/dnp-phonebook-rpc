from generated import phonebook_pb2
from generated import phonebook_pb2_grpc
from phonebook.signing import canonical_contact, canonical_contacts, sign_payload
from phonebook.storage import PhonebookStorage


class PhonebookService(phonebook_pb2_grpc.PhonebookServiceServicer):

    def __init__(self, storage: PhonebookStorage):
        self.storage = storage

    def AddContact(self, request, context):
        try:
            message = self.storage.add_contact(request.name, request.phone)
            return phonebook_pb2.OperationStatus(
                success=True,
                message=message
            )
        except ValueError as error:
            return phonebook_pb2.OperationStatus(
                success=False,
                message=str(error)
            )

    def LookupContact(self, request, context):
        try:
            name = request.name.strip()
            phone = self.storage.lookup_contact(name)

            payload = canonical_contact(name, phone)
            signature = sign_payload(payload)

            return phonebook_pb2.LookupContactResponse(
                success=True,
                message="Contact found",
                contact=phonebook_pb2.Contact(
                    name=name,
                    phone=phone
                ),
                signature=signature
            )
        except (ValueError, KeyError) as error:
            return phonebook_pb2.LookupContactResponse(
                success=False,
                message=str(error),
                signature=""
            )

    def ListContacts(self, request, context):
        contacts = self.storage.list_contacts()

        payload = canonical_contacts(contacts)
        signature = sign_payload(payload)

        return phonebook_pb2.ListContactsResponse(
            contacts=[
                phonebook_pb2.Contact(name=name, phone=phone)
                for name, phone in sorted(contacts.items())
            ],
            signature=signature
        )
