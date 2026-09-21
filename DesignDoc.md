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
4. apply edits to documents
5. maintain subscribers for each document
6. send updates to subscribed clients whenever a document changes. for now lets keep it within 0.5 seconds. 
7. whenever multiple edits onto theh same document, handle in that specific order i.e. the order doesnt matter however they should be atomic. it should not be corrupted. 
8. the server address should be accepted as a command-line argument. 
- the server should implement and give access to these apis.
11. for now,w whenver a client creates a document with an already existing name, do not allow it to create a document. in future, give it two options, allow it to replace the content of the old file with the new content or just change the name. do this only if the file had been created by the same client in the past. 
12. what if a client created a file and left the network, never to be contacted again? here we do not care about the scenario for now. maybe we just let do not allow the server to create a new a file with the same name.
13. by editing, deletion is not supported. we only support appending at certain positions. 
### APIs
1. CreateDocument(CreateDocumentRequest) -> CreateDocumentResponse: Creates a new document with a unique name and initial content
2. GetDocument(GetDocumentRequest) -> GetDocumentResponse: returns the contents of a document. 
3. EditDocument(EditDocumentRequest) -> EditDocumentResponse: inserts text at a specified position in an existing document.
4. SubscribeToUpdates(UpdateRequest) -> stream DocumentUpdate: allows a client to subscribe to a document. Whenever the document is modified, the server send the updated content to all the subscribed clients.

## High level design
### server
#### createDocument
1. The server should create maintain a table/dictionary. key is the file name. value is the content of the file whichis a string. i think storing a pointer to the location of the file is a better idea. 
2. everytime a new file creation comes, it should cross check against the existing keys. if it already exists, send an error saying file name already exists. 
3. the client should send the name of the doc and content. the content is optional
#### getDocument
1. the client should send the server the name of the document. 
2. the server should respond with the name of the document and the content of the document. 
3. if the document doesn't exist, the server should say so. 

#### editDocument(EditDocumentRequest)
1. the client should mention the document name, the position, and the content which should be added. 
2. we do not do deletion of content.
3. if two servers send edits at approximately the same time, then we process them in whatever order we receive. 
4. if the document doesn't exist, the server will say so. 

#### subscribeToUpdates(UpdateRequest)
1.  the client should be allowed to input a file name as part of this request and the server should push the updated file to the clients. 
2. we should maintain another list which contaisn keys to list of clients which subscribed. we should push accordingly. 


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

## on how to implement subscribe
The subscribe function has a data structure where the keys are the names of the files and the value is a list of queues. each queue acts as the buffer for the producer consumer pattern where whenever the document is edited, for each element in the queue the server adds the new stuff(yields stuff) onto the queue which is conveyed to the client whos queue that is. 

the subscribe function has a while true function which yields whenever some document is changed. it is being called whenever some edit happens on a file, then we yield the new content onto the queues in the stream and let gRPC send them to the client. 
