

<h1 align=center>DocEdit: gRPC Collaborative Document Editor<h1>

## What is this? (Simple Description)

DocEdit is a lightweight, real-time collaborative text editor built entirely for the terminal. It allows multiple users to connect to a central server, create text files, and edit them together. If you subscribe to a document, any edit made by another user will instantly stream to your screen. Think of it as a highly simplified, command-line version of Google Docs.

## Features

* **Create & Retrieve:** Create new documents and fetch existing content.
* **Targeted Edits:** Insert text at specific index positions within the document.
* **Live Collaboration:** Subscribe to a document to receive real-time, streaming updates when anyone else makes an edit.
* **Atomic Updates:** Edits happening at the exact same time are handled safely without corrupting the document text.

## How to Run

### 1. Prerequisites

You need Python installed, along with the gRPC libraries. To install the necessary requirements, please run the following command

```bash
pip install -r requirements.txt

```

### 2. Compile the Protocol Buffers(optional)

If you modify `routeGuide.proto`, you must recompile the gRPC boilerplate code before running the server or client:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. routeGuide.proto

```

### 3. Start the Server

Open a terminal and start the centralized server. It will run in the background and listen on port `50051`.

```bash
python server.py

```

### 4. Run the Client

Open one (or multiple!) new terminal windows to act as your users.

```bash
python client.py

```

**Available CLI Commands:**

* `create <filename> <optional_content>` (e.g., `create notes.txt "Hello"`)
* `get <filename>` (e.g., `get notes.txt`)
* `edit <filename> <position> <content>` (e.g., `edit notes.txt 5 " World"`)
* `subscribe <filename>` (e.g., `subscribe notes.txt`)
* `exit` (Closes the client)

---

## Technical Architecture

DocEdit is built on a distributed client-server architecture utilizing **gRPC** and **Protocol Buffers (Protobuf)** over HTTP/2.

### 1. State Management

The server is strictly stateful and maintains all data in-memory to ensure ultra-low latency. It relies on two primary Hash Maps (Python Dictionaries):

* `documents`: Maps the document name to its raw string content.
* `subscribers`: Maps the document name to a list of thread-safe `queue.Queue()` objects, representing the active network streams of subscribed clients.

### 2. Concurrency & Thread Safety

Because the gRPC Python server automatically spawns a new thread for every incoming client request, the system implements a **Global Lock** (`threading.Lock`) to prevent race conditions.

* **TOCTOU Prevention:** The lock is acquired *before* dictionary lookups to prevent Time-Of-Check to Time-Of-Use vulnerabilities.
* **Atomic Modifications:** Simultaneous `editDocument` RPCs are forced to process sequentially, ensuring string manipulations do not overwrite one another.
* **Ordered Dispatch:** The lock is held until the compiled Protobuf update is successfully pushed to all subscriber queues, guaranteeing that the order of edits executed on the server matches the exact order of updates streamed to the clients.

### 3. Streaming Pipeline (Producer/Consumer)

Live updates are achieved using gRPC Server-Streaming RPCs paired with a Producer/Consumer threading pattern.

* **The Producer (`editDocument`):** Upon a successful edit, the executing thread constructs a `documentUpdate` Protobuf message and executes a non-blocking `.put()` into the queue of every subscribed client.
* **The Consumer (`subscribeToUpdates`):** When a client subscribes, the server traps that specific thread in a generator loop. The thread uses a blocking `.get()` call on its assigned queue. This instructs the OS to put the thread to sleep, consuming 0% CPU, until the Producer injects data.
* **Client-Side Daemon:** To prevent the streaming server responses from freezing the client's terminal UI, the client spawns a background `daemon=True` thread specifically to listen to the gRPC stream and print live updates asynchronously.

### 4. Memory Leak Mitigation

If a client abruptly disconnects (e.g., network failure, hard exit), their gRPC stream dies, but their `queue.Queue` remains in the server's memory. To prevent Out-Of-Memory (OOM) crashes, the `subscribeToUpdates` consumer validates `context.is_active()` whenever it wakes up. If the connection is dead, the server safely acquires the global lock, removes the client's queue from the subscriber list, and terminates the thread.

