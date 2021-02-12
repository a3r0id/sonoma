
"""
SONOMA/1.0.8
"""
__version__ = '1.0.8'
# 2021 github.com/hostinfodev

import socket
import threading
from http import HTTPStatus
from logging import basicConfig
import email.utils as eut

class defaults:
    httpVersion = "1.1" # DONT CHANGE THIS UNLESS YOU KNOW EXACLTY WHAT YOU ARE DOING!
    serverName = "Sonoma/" + __version__ # SERVER NAME/VERSION. THIS WILL SHOW IN THE RESPONSE HEADER TO VISITORS. YOU CAN CHANGE THIS TO ANYTHING.
    defaultOrigin = "*" # DEFAULT ORIGIN HEADER. THE HEADER WILL DISPLAY THIS VALUE UNLESS OTHERWISE CHANGED IN YOU CUSTOM HANDLER.
    # DEFAULT RESPONSE FOR DEFAULT HANDLER, YOU ARE ENCOURAGED TO CHANGE THIS IF YOU ARE NOT USING A CUSTOM HANDLER.
    defaultResponse = """ 
        <!DOCTYPE html><html><head>
        <style>html, body{ margin: 0 auto;text-align:center; }</style>
        </head><body>
        <h1 style=\"text-align:center;\">Hello World!</h1>
        <span>This is the default webpage for %s.</span>
        </body></html>
        """ % serverName 

def defaultHandler(self, requestStatusLine, requestHeaders, requestBody, client_connection, client_address):
    """
    ## Supported Methods:
    - GET
    - HEAD
    """
    
    # SERVE GET
    if requestStatusLine.split()[0].lower() == "get":
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.OK, contentType="html")
        responseBody = defaults.defaultResponse
        return (responseStatusLine, responseHeaders, responseBody)

    # SERVE HEAD
    elif requestStatusLine.split()[0].lower() == "head":   
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.OK, contentType="text")
        return (responseStatusLine, responseHeaders, "")  
    
    # RESPOND WITH 405 STATUS - METHOD NOT ALLOWED
    else:
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.METHOD_NOT_ALLOWED, contentType="text")
        return (responseStatusLine, responseHeaders, "")    

SERVER_THREADS = []

basicConfig()

class httpServer(object):
    """
    ```python
    httpServer(string address, int port, function handler=None)
    ```
    """
    def __init__(self, address, port, handler=None) -> None:

        # HANDLER ASSIGNMENT
        self.handler = handler

        # GET DEFAULT HANDLER
        self.defaultHandler = defaultHandler

        # GET CLIENT ADDRESS
        self.vector = (address, port)
        
        # SET CONTENT TYPES DICT
        self.contentTypes = {
            'json': 'application/json',
            'text': 'text/plain',
            'html': 'text/html'
        }
        
        # DEFINE THE SOCKET
        self.sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # METHOD FOR GETTING HTTP RESPONSE HEADERS AND STATUSLINE
    def httpHeaders(self, httpStatus, origin="*", contentType="text"):

        # SETS CONTENT TYPE IF FOUND ELSE SETS VALUE TO THE CONTENTTYPE VARIABLE
        if contentType in self.contentTypes:
            contentType = self.contentTypes[contentType]

        # GET TIMESTAMP NOW, FORMATTED BY IETF STANDARDS 
        date = str(eut.formatdate())
        date = date.replace(date.split(' ')[5], "GMT")

        # RETURNS (responsestatusLine, [headers])
        return ( f"HTTP/{defaults.httpVersion} {httpStatus.value} {httpStatus.phrase}\r\n",
        [
            f"Access-Control-Allow-Origin: {origin}",
            "Connection: Close",
            #"Content-Encoding: gzip",
            f"Content-Type: {contentType}",
            f"Date: {date}",
            f"Last-Modified: {date}",
            f"Server: {defaults.serverName}",
            "Vary: Cookie, Accept-Encoding",
            "X-Frame-Options: DENY"
        ])

    # UTILITY METHOD THAT SETS A CUSTOM HANDLER
    def set_handler(self, handler):
        """
        # Required format for custom handler:
        
        - Parameters
        ```
        myHandler(self, str requestStatusLine, list requestHeaders, bytes or str requestBody, socket.socket clientConnection, tuple clientAddress)
        ```
        - Return Value
        ```
        return (str responseStatusLine, list responseHeaders, bytes or str responseBody)
        ```
        """
        self.handler = handler
    
    # START SERVER THREAD
    def run(self):
        # SERVER THREAD
        def thread():            
            self.sock_.bind(self.vector)
            self.sock_.listen(1)

            print('Listening on %s:%s ...' % self.vector)

            # [*i*] USE self.sock.close to close entire server socket. [*i*] 
            while True:    

                # Wait for client connections
                client_connection, client_address = self.sock_.accept()

                # Get the client request
                try:
                    request = client_connection.recv(1024).decode()
                except:
                    client_connection.close()
                    continue

                requestHeaders_buffer = request.split("\r\n")

                try:
                    requestBody = request.split('\r\n\r\n')[1]
                except:
                    requestBody = ""
                    
                try:
                    requestStatusLine = requestHeaders_buffer.pop(0)
                except:
                    client_connection.close()
                    continue

                requestHeaders = []
                for unit in requestHeaders_buffer:
                    if unit != "" and ": " in unit:
                        requestHeaders.append([unit.split(': ')[0], unit.split(': ')[1]])
        
                # PROCESS REQUEST - VOID
                if self.handler is not None:
                    responseStatusLine, responseHeaders, responseBody = self.handler(self, requestStatusLine, requestHeaders, requestBody, client_connection, client_address)

                else:
                    responseStatusLine, responseHeaders, responseBody = self.defaultHandler(self, requestStatusLine, requestHeaders, requestBody, client_connection, client_address)
                
                if len(responseBody):
                    responseHeaders.append(f'Content-Length: {str(len(responseBody))}')    
                
                response = responseStatusLine + ("\r\n".join(responseHeaders)) + "\r\n\r\n" + responseBody
                
                client_connection.sendall(response.encode())

                client_connection.close()

        
        t = threading.Thread(target=thread)
        t.start()
        SERVER_THREADS.append(t)












