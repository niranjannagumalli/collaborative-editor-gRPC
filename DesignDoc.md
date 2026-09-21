# DocEdit

## Objective
Build a multi-user collaborative document editing system using gRPC. 

## Background
This project tackles the problem of multiple users trying collaborate in real time by working on the same document. The goal of the project is to maintain one copy of the document at the server and send the modifications made by a user to all other users who are subscribed to that document.  

## Goals and non Goals
- We should have one process which acts as a server and it should be able to handle multiple clients. 
- Clients are also processes. They should provide these options
### Goals for clients
1. Create Documents
2. Open Documents
3. Edit Documents
4. Subscribe to updates
5. Exit

### Goals for server
1. the server should maintain the documents in memory. 
2. handle requests from multiple clients
3. create and retrieve documents
4. apply edits to documents. edit means that one can append at a certain position. 
5. maintain subscribers for each document
6. the server address should be accepted as a command-line argument. 
- the server should implement and give access to these apis.

7. whenever multiple edits onto theh same document, handle in that specific order i.e. the order doesnt matter however they should be atomic. it should not be corrupted. 


### APIs
1. CreateDocument(CreateDocumentRequest) -> CreateDocumentResponse: Creates a new document with a unique name and initial content
2. GetDocument(GetDocumentRequest) -> GetDocumentResponse: returns the contents of a document. 
3. EditDocument(EditDocumentRequest) -> EditDocumentResponse: inserts text at a specified position in an existing document.
4. SubscribeToUpdates(UpdateRequest) -> stream DocumentUpdate: allows a client to subscribe to a document. Whenever the document is modified, the server send the updated content to all the subscribed clients.

## High level design
### server
#### createDocument
1. The server should create maintain a table/dictionary. key is the file name. value is the content of the file whichis a string. 
2. everytime a new file creation comes, it should cross check against the existing keys. if it already exists, send an error saying file name already exists. 
3. the client should send the name of the doc and content. the content is optional
#### getDocument
1. the client should send the server the name of the document. 
2. the server should respond with the name of the document and the content of the document. 
3. if the document doesn't exist, the server should say so. 

#### editDocument(EditDocumentRequest)

1. acquire a lock, check if the docname is valid. use python's with keyword and put the lines of code which does the job till step 5 in the block inside with. 

2. if the document doesn't exist, the raise error code and release the lock
3. if valid:
    
    change the string associated with that file name
4. maintain a global datastructure which contains key as file name. and a list of queues, each corresponding to the queues which belong to the clients subscribed to the respective file. 
5. here this function, after updating the file at the server, does its duty as the producer of the producer/consumer pattern, puts() the new string (in the valid protobuf format) into the queues which are in the dict which has the file name as the key  
6. release the lock. 

#### subscribeToUpdates(UpdateRequest)
1. check if the file name is valid. return error code if invalid
2. add a queue to the streaming dict. streaming dict contains file names as the keys and list of queues as values. 
3. now enter the while true loop. 
4. just use queue.get(), it will yield the data if it is there, else it will be blocked. 
5. after yielding, it will check if the client is still active. use gRPC's context.is_active() for this.  if the client is not active, then we can remove the queue out of the list and break out of the loop. 

#### exit(for the clients)
1. on running exit, close the gRPC connection. 

## IDL and datastructures
1. rpc createDocument(createDocumentRequest) returns (createDocumentResponse)
2. rpc getDocument(getDocumentRequest) returns (getDocumentResponse)
3. rpc editDocument(editDocumentRequest) returns (editDocumentResponse)
4. rpc subscribeToUpdates(updateRequest) returns (stream documentUpdate)

```
message createDocumentRequest
{
    string docName = 1;
    string content = 2;
}
```
```
message createDocumentResponse
{
    string result = 1;
}
```
```
message getDocumentRequest
{
    string docName = 1;
}
```
```
message getDocumentResponse
{
    string docName = 1;
    string content = 2;
    
}
```
```
message editDocumentRequest
{ 
    string docName = 1;
    string content = 2;
    int32 position = 3;
}
```

```
message editDocumentResponse
{
    string docName = 1;
    string content = 2;
    
}
```
```
message updateRequest
{
    string docName = 1;
}
```
```
message documentUpdate
{
    string docName = 1;
    string content = 2;
    
}
```
The server maintains a dictionary with the file name as the key and the content as the value. 
The server maintains another table with the file name as the key and the list of clients subscribed to it as the value. 

### gRPC status codes
We will use error codes in the result section  to ensure better communication
| Code | Number | Description |
|---|---|---| 
| OK           | 0 | whenever the operation is successfull| 
| UNAVAILABLE | 14 | if the server is down|
| OUT_OF_RANGE| 11| whenever a client tries to edit a file at a position which is out of bounds|
| ALREADY_EXISTS| 6  | whenever a client tries to create a file which already exists|
|NOT_FOUND      | 5 | whenever a client tries to get/subscribe to a file which is not present |
|UNIMPLEMENTED | 12| when the client tries to invoke a method which is not implemented. |


suppose, if the server realises that the given insertion is out of bounds of the file, it'll raise an error and return the above necessary error code instead.

