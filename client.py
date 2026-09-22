import grpc
import threading
import sys

import routeGuide_pb2_grpc
import routeGuide_pb2

def listen_for_updates(stub, doc_name):
    """
    this func will run in a background thread.
    it needs to call subscribeToUpdates RPC and print incoming data
    """

    print(f"\n[Subscribed to {doc_name} in background]")

    request = routeGuide_pb2.updateRequest(docName=doc_name)

    stream = stub.subscribeToUpdates(request)

    try:
        for update in stream:
            print(f"\n[LIVE UPDATE - {update.docName}]: {update.content}")
            print("> ", end="", flush=True)
    except grpc.RpcError as e:
        print(f"stream disconnected: {e.details()}")
    

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = routeGuide_pb2_grpc.RouteGuideStub(channel)

    print("DocEdit Client Started.")
    print("Commands: create <name> <content>, get <name>, edit <name> <pos> <content>, subscribe <name>, exit ")

    while True:
        try:
            raw_input = input("> ").strip()
            if not raw_input:
                continue
            parts = raw_input.split(" ", 3)
            command = parts[0].lower()

            if command == "create":
                name = parts[1]
                content = parts[2] if len(parts) > 2 else ""
                
                createDoc = routeGuide_pb2.createDocumentRequest(docName=name, content=content)
                response = stub.createDocument(createDoc)
                print(response.result)
            elif command == "get":
                name = parts[1]

                getDoc = routeGuide_pb2.getDocumentRequest(docName=name)

                response = stub.getDocument(getDoc)
                print(response.content)

            elif command == "edit":
                name = parts[1]
                position = int(parts[2])
                content = parts[3]

                editDoc = routeGuide_pb2.editDocumentRequest(docName=name, content=content, position=position)
                response = stub.editDocument(editDoc)

                print(response.content)

            elif command == "subscribe":
                name = parts[1]

                listenerThread = threading.Thread(
                    target=listen_for_updates,
                    args=(stub, name), 
                    daemon=True
                )
                listenerThread.start()

            elif command == "exit":
                print("exiting, goodbye!")
                break
            else:
                print("unknown command. Commands: create <name> <content>, get <name>, edit <name> <pos> <content>, subscribe <name>, exit ")                

        except grpc.RpcError as e:
            print(f"\n[Server Error]: {e.code().name} - {e.details()}")
        except Exception as e:
            print(f"\n[Client error]: {e}")

if __name__ == '__main__':
    run()
