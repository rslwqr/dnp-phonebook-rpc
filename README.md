# Phonebook Lookups with RPC (gRPC)

This project implements a distributed phonebook service using RPC (gRPC).  
Clients can remotely manage contact information stored on the server.

---

## Features

- Add new contacts  
- Lookup contacts by name  
- Update phone numbers  
- Delete contacts  
- List all contacts  
- Support for concurrent client requests  

---

##  Architecture

The system follows a client-server architecture:

- **Client** — sends RPC requests  
- **Server** — processes requests  
- **Service Layer** — connects RPC with business logic  
- **Storage** — in-memory phonebook  

---

## Technologies

- Python  
- gRPC  
- Protocol Buffers  

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

---

## Running the system

### Start server

```bash
python server.py
```

Expected output

```bash
Server started on port 50051
```

Then use the menu to interact with the system.

---

## Usage

After starting the server and client, the user can interact with the system through a simple command-line menu.

Available actions:

1. Add contact — enter name and phone number  
2. Lookup contact — find a contact by name  
3. Update contact — change phone number  
4. Delete contact — remove a contact  
5. List contacts — display all stored contacts  
6. Exit — close the client  

### Example

```text
1. Add contact
2. Lookup contact
3. Update contact
4. Delete contact
5. List contacts
6. Exit

Choose an option: 1
Enter name: Alice
Enter phone: 12345

Contact 'Alice' added
```

---

## Testing

### Run all tests

```bash
pytest
```

### Expected result:

```bash
19 passed
```


## Concurrency

The system supports multiple clients simultaneously:

- ThreadPoolExecutor is used in the server  
- Lock is used in storage to ensure thread safety  

---

## Notes

- Data is stored in memory  
- No database is used  
- The system is designed for simplicity and low latency

## Links for report and DemoVideo

- [Demo Video](https://your-video-link-here](https://drive.google.com/file/d/18A1RCoJKrTeRxt4M2OfhAQoAVd_brl28/view?usp=sharing)
- [Report (PDF)](https://your-pdf-link-here](https://drive.google.com/file/d/1XHWzoVZ5qA6jWIxL2CYz6ni4r3faAs8c/view?usp=sharing)

