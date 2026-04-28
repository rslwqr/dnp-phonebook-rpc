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

