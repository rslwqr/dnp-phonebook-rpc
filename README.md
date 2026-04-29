# Phonebook Lookups with RPC (gRPC)

This project implements a distributed write-once phonebook service using RPC (gRPC).  
Clients can remotely add and query contact information stored on the server.  
The server returns signed lookup data so that clients can verify response integrity.

---

## Features

- Add new contacts  
- Lookup contacts by name  
- List all contacts  
- Write-once storage: existing contacts cannot be updated or overwritten  
- Signed server responses for verification  
- Support for concurrent client requests  

---

##  Architecture

The system follows a client-server architecture:

- **Client** — sends RPC requests and verifies signed responses  
- **Server** — processes requests and returns signed data  
- **Service Layer** — connects RPC methods with business logic  
- **Storage** — thread-safe in-memory write-once phonebook  
- **Signing Layer** — creates and verifies HMAC-SHA256 signatures  

---

## Technologies

- Python  
- gRPC  
- Protocol Buffers  
- HMAC-SHA256 for response signing  

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/rslwqr/dnp-phonebook-rpc.git
cd dnp-phonebook-rpc
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate gRPC code (if needed)

```bash
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./generated \
    --grpc_python_out=./generated \
    ./proto/phonebook.proto
```

If the generated file `generated/phonebook_pb2_grpc.py` contains this import:

```python
import phonebook_pb2 as phonebook__pb2
```

replace it with:

```python
from generated import phonebook_pb2 as phonebook__pb2
```

---

## Running the system

### Start server

```bash
python server.py
```

Expected output

```bash
Write-once phonebook server started on port 50051
```

### Start client

Open another terminal, activate the virtual environment, and run:

```bash
python client.py
```

Then use the menu to interact with the system.

---

## Usage

After starting the server and client, the user can interact with the system through a simple command-line menu.

Available actions:

1. Add contact — enter name and phone number  
2. Lookup contact — find a contact by name and verify the signed response  
3. List contacts — display all stored contacts and verify the signed list response  
4. Exit — close the client  

Important: this is a write-once phonebook.  
After a contact is added, it cannot be updated, deleted, or overwritten.

### Example

```text
Write-once Phonebook Client Menu:
1. Add contact
2. Lookup contact
3. List contacts
4. Exit

Choose an option: 1
Enter name: Alice
Enter phone: 12345

Contact 'Alice' added
```

Lookup example:

```text
Choose an option: 2
Enter name to lookup: Alice

Name: Alice, Phone: 12345
Signature: 8f2c...
Signature valid: True
```

Duplicate add example:

```text
Choose an option: 1
Enter name: Alice
Enter phone: 99999

Contact 'Alice' already exists; write-once phonebook does not allow overwrites
```

---

## Testing

### Run all tests

```bash
pytest
```

or:

```bash
python -m pytest -q
```

### Expected result:

```bash
24  passed
```

The test suite validates:

- storage correctness  
- write-once behavior  
- signature generation and verification  
- concurrent access to storage  
- concurrent RPC requests  

## Concurrency

The system supports multiple clients simultaneously:

- `ThreadPoolExecutor` is used in the gRPC server  
- `Lock` is used in storage to ensure thread safety  
- Concurrent add and lookup operations are covered by tests  
- Duplicate concurrent inserts are handled safely: only one insert succeeds  

---

## Notes

- Data is stored in memory  
- No database is used  
- The phonebook is write-once: contacts cannot be updated or deleted after insertion  
- Lookup and list responses are signed by the server  
- The client verifies signatures to detect tampered data  
- The system is designed for simplicity, correctness, and low latency  

## Links for report and DemoVideo

- [Demo Video](https://drive.google.com/file/d/18A1RCoJKrTeRxt4M2OfhAQoAVd_brl28/view?usp=sharing)
- [Report (PDF)](https://drive.google.com/file/d/1XHWzoVZ5qA6jWIxL2CYz6ni4r3faAs8c/view?usp=sharing)
