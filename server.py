from concurrent import futures
import grpc
import threading
import queue

import routeGuide_pb2
import routeGuide_pb2_grpc

class RouteGuideServicer(routeGuide_pb2_grpc.RouteGuideServicer):
    def __init__(self):
        self.documents = {}
        self.subscribers = {}

        self.global_lock = threading.Lock()

    def createDocument(self, request, context):
        fileName = request.docName
        content = request.content
        with self.global_lock:
            if fileName in self.documents:
                #raise an error
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Document already exist. ")
                context.abort()
            else:
                self.documents[fileName] = content
                return routeGuide_pb2.createDocumentResponse(result="Document created successfully!")
        

    def getDocument(self, request, context):
        fileName = request.docName

        with self.global_lock:
            if fileName in self.documents:
                return routeGuide_pb2.getDocumentResponse(docName=fileName, content=self.documents[fileName])

            else:
                #raise an error
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Document doesn't exist. ")
                context.abort()
        
            
    def editDocument(self, request, context):
        fileName = request.docName
        newString = request.content
        position = request.position

        with self.global_lock:
            if fileName not in self.documents:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Document doesn't exist")
                context.abort()
            else:
                oldString = self.documents[fileName]
                if position > len(oldString):
                    context.set_code(grpc.StatusCode.OUT_OF_RANGE)
                    context.set_details("You tried to edit a position out of range")
                    context.abort()
                else:
                    updatedString = oldString[:position] + newString + oldString[position:]
                    self.documents[fileName] = updatedString
                    response = routeGuide_pb2.documentUpdate(docName=fileName, content=self.documents[fileName], )
                    if fileName in self.subscribers:

                        for _ in self.subscribers[fileName]:
                            _.put(response)
                    return routeGuide_pb2.editDocumentResponse(docName=fileName, content=self.documents[fileName], )


    def subscribeToUpdates(self, request, context):
        fileName = request.docName

        with self.global_lock:
            
            if fileName not in self.documents:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Document doesn't exist")
                context.abort()
            tempQ = queue.Queue()
            if fileName not in self.subscribers:
                self.subscribers[fileName] = []    
            self.subscribers[fileName].append(tempQ)

        while True:

            if not context.is_active():
                with self.global_lock:
                    self.subscribers[fileName].remove(tempQ)
                    break
            updateMessage = tempQ.get()
            yield updateMessage


            

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    routeGuide_pb2_grpc.add_RouteGuideServicer_to_server(RouteGuideServicer(), server)

    server.add_insecure_port('[::]:50051')

    print("server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()