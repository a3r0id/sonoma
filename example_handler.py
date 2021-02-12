from sonoma import defaultHandler, httpServer

server = httpServer('127.0.0.1', 8888)

server.handler = defaultHandler

server.run()