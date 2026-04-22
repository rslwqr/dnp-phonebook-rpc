from generated import phonebook_pb2
from generated import phonebook_pb2_grpc
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
        except ValueError as e:
            return phonebook_pb2.OperationStatus(
                success=False,
                message=str(e)
            )

    def LookupContact(self, request, context):
        try:
            phone = self.storage.lookup_contact(request.name)
            return phonebook_pb2.LookupContactResponse(
                success=True,
                message="Contact found",
                contact=phonebook_pb2.Contact(
                    name=request.name,
                    phone=phone
                )
            )
        except (ValueError, KeyError) as e:
            return phonebook_pb2.LookupContactResponse(
                success=False,
                message=str(e)
            )

    def UpdateContact(self, request, context):
        try:
            message = self.storage.update_contact(request.name, request.new_phone)
            return phonebook_pb2.OperationStatus(
                success=True,
                message=message
            )
        except (ValueError, KeyError) as e:
            return phonebook_pb2.OperationStatus(
                success=False,
                message=str(e)
            )

    def DeleteContact(self, request, context):
        try:
            message = self.storage.delete_contact(request.name)
            return phonebook_pb2.OperationStatus(
                success=True,
                message=message
            )
        except (ValueError, KeyError) as e:
            return phonebook_pb2.OperationStatus(
                success=False,
                message=str(e)
            )

    def ListContacts(self, request, context):
        contacts = self.storage.list_contacts()

        return phonebook_pb2.ListContactsResponse(
            contacts=[
                phonebook_pb2.Contact(name=name, phone=phone)
                for name, phone in contacts.items()
            ]
        )