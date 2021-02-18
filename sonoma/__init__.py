
__version__ = '1.0.11'
__version_formal__ = f"SONOMA/{__version__}"
# 2021 github.com/hostinfodev

# TODO: IS SERVER BLOCKING :O ?
# -> YES! FIX THIS!

from datetime import date
import socket
from threading import Thread, Lock
from http import HTTPStatus
import email.utils as eut
from sys import stdout
from datetime import datetime
from time import tzname

# RETURNS HTTP-FRIENDLY GMT TIMESTAMP
def serverGmtTime():
    a = str(eut.formatdate())
    b = a.replace(a.split(' ')[5], "GMT")
    return b

# RETURNS HTTP-FRIENDLY LOCAL TIMESTAMP
def serverLocalTime(tupleWithTimeZone = False):
    tme = datetime.now()
    a = str(eut.formatdate(tme.timestamp()))
    # IS TRUE, RETURNS TUPLE INCLUDING TIMEZONE
    # TODO: GET ABBREVIATION FOR TZ INSTEAD
    if tupleWithTimeZone:
        return (a, tzname)
    return a    

# REQUEST-TYPES: FOR FUTURE USE...
class requestTypes:
    GET = {
        'verb': "GET",
        'body': True,
        'addedHeaders': []
        }
    POST = {
        'verb': "POST",
        'body': True,
        'addedHeaders': []
        }
    HEAD = {
        'verb': "HEAD",
        'body': False,
        'addedHeaders': []
        }
    OPTIONS = {
        'verb': "OPTIONS",
        'body': False,
        'addedHeaders': [
            ['Allow', '\\%\\options\\%\\']
        ]
        }

# FOR HANDLING MULTIPLE SERVER OBJECT INSTANCES
SERVER_THREADS = []
SERVER_THREADS_LOCK = Lock()

# DEFAULT CONFIGURATION
defaults = {
    'httpVersion': "1.1", # DONT CHANGE THIS UNLESS YOU KNOW EXACLTY WHAT YOU ARE DOING!
    'serverName': "Sonoma/" + __version__, # SERVER NAME/VERSION. THIS WILL SHOW IN THE RESPONSE HEADER TO VISITORS. YOU CAN CHANGE THIS TO ANYTHING.
    'defaultOrigin': "*", # DEFAULT ORIGIN HEADER. THE HEADER WILL DISPLAY THIS VALUE UNLESS OTHERWISE CHANGED IN YOU CUSTOM HANDLER.
    'maxHeaderKeyLength': 1024,
    'maxHeaderValueLength': 8192,
    'maxRecv': 1024,
    'maxCookieLen': 8192, # ENTIRE COOKIE STRING'S MAXIMUX LENGTH.
    # DEFAULT RESPONSE FOR DEFAULT HANDLER, YOU ARE ENCOURAGED TO CHANGE THIS IF YOU ARE NOT USING A CUSTOM HANDLER.
    'defaultResponse': b"""<!DOCTYPE html><html><head>
<style>html, body{ margin: 0 auto;text-align:center; }</style>
</head><body>
<h1 style=\"text-align:center;\">Hello World!</h1>
<span>This is the default webpage for %s.</span>
</body></html>""" % __version_formal__.encode()
}

# PARSES COOKIES FROM HEADER-ARRAY, RETURNS OUR CUSTOM COOKIEJAR FOR USE OF A HANDLER.
# RETURNS -> {'cookieName': "cookieValue", 'cookieName': "cookieValue"}
def parseCookies(requestHeaders): 
    """
    RETURNS -> {'cookieName': "cookieValue", 'cookieName': "cookieValue"}
    """
    requestCookies = {} 
    for header in requestHeaders:
        if header[0] == 'Cookie':
            ckBuf = header[1].split('; ')
            if len(ckBuf):
                for cookie in ckBuf:
                    if '=' in cookie:
                        ckPrs = cookie.split('=')
                        if len(ckPrs) >= 2:
                            requestCookies[ckPrs[0]] = ckPrs[1]
            break
    return requestCookies    

# UTILITY TO SIMPLY SET A COOKIE TO A HEADER-ARRAY, FOR USE INSIDE OF A HANDLER.
def setCookie(headerArray, cookieName, cookieValue, attributes):
    cookieBuffer = "Set-Cookie: %s=%s" % (cookieName, cookieValue,)
    attributesBuffer = ""
    if len(attributes):
        cookieBuffer += '; '
        if len(attributes) > 2:
            attributesBuffer = "; ".join(attributes)
        else:
            cookieBuffer += attributes[0]
    headerArray.append(cookieBuffer + attributesBuffer)

# UTILITY TO SIMPLY ADD A HEADER TO AN HEADER-ARRAY, FOR USE INSIDE OF A HANDLER.
def addResponseHeader(headerArray, key, value):
    headerArray.append("%s: %s" % (key, value,))

# OUR BASIC, THREAD-SAFE PRINT-FUNCTION
def sonomaPrint(string):
    SERVER_THREADS_LOCK.acquire()
    stdout.write('\n' + str(string))
    SERVER_THREADS_LOCK.release()

def errorResponse(self, _HTTPStatus, CONNECTION):
    """
    # Sends Error Response - (void)
    ```python
    errorResponse(self, _HTTPStatus, CONNECTION)
    ```
    """
    responseStatusLine, _ = self.httpHeaders(_HTTPStatus, contentType="text")
    client_connection, _ = CONNECTION

    # CREATE THE RESPONSE
    response = responseStatusLine
    
    # SEND THE RESPONSE
    client_connection.sendall(response.encode())

    # CLOSE THE CLIENT'S SOCKET
    client_connection.close()

# REQUEST = (requestStatusLine, requestHeaders, requestBody,)
# CONNECTION = (client_connection, client_address,)
def defaultHandler(self, REQUEST, CONNECTION):
    """
    # Supported Methods:
    - GET
    - HEAD
    - OPTIONS
    """

    # UNPACK "REQUEST" TUPLE 
    requestStatusLine, requestHeaders, requestBody = REQUEST

    # UNPACK CONNECTION TUPLE
    client_connection, client_address = CONNECTION
    
    # LOG THE REQUEST
    sonomaPrint("%s -> %s Request: %s" % (str(self.vector), str(client_address), str(requestStatusLine),))

    # SERVE GET
    if requestStatusLine.split()[0].lower() == "get":
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.OK, contentType="html")
        responseBody = defaults['defaultResponse']
        return (responseStatusLine, responseHeaders, responseBody)

    # SERVE HEAD
    elif requestStatusLine.split()[0].lower() == "head":   
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.OK, contentType="text")
        return (responseStatusLine, responseHeaders, "")  
    
    # SERVE OPTIONS
    elif requestStatusLine.split()[0].lower() == "options":   
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.OK, contentType="text")
        return (responseStatusLine, responseHeaders, "")  

    # RESPOND WITH 405 STATUS - METHOD NOT ALLOWED 
    else:
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.METHOD_NOT_ALLOWED, contentType="text")
        return (responseStatusLine, responseHeaders, "")
            
class httpServer(object):
    """
    ```python
    httpServer(str address, int port, function handler=None)
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

        # SETS CONTENT TYPE IF FOUND ELSE SETS VALUE TO THE CONTENTTYPE DEFAULT
        if contentType in self.contentTypes:
            contentType = self.contentTypes[contentType]

        # GET TIMESTAMP NOW, FORMATTED BY IETF STANDARDS 
        date = serverGmtTime()

        # RETURNS (responsestatusLine, [headers])
        return ( f"HTTP/{defaults['httpVersion']} {httpStatus.value} {httpStatus.phrase}\r\n",
        [
            f"Access-Control-Allow-Origin: {origin}",
            "Connection: Close",
            #"Content-Encoding: gzip",
            f"Content-Type: {contentType}",
            f"Date: {date}",
            f"Last-Modified: {date}",
            f"Server: {defaults['serverName']}",
            "Vary: Cookie, Accept-Encoding",
            "X-Frame-Options: DENY"
        ])

    def editConfig(self, **editParams):
        """
        # Edits configuration for Server-Object.
        ## (Equivalent to `defaults['foo'] = 'bar'`) but won't set the value unless its already existing.
        ```python
        server.editConfig(self, str httpVersion=None, str serverName=None, str defaultOrigin=None, int maxHeaderKeyLength=None, int maxHeaderValueLength=None, int maxRecv=None, str or bytes defaultResponse=None)
        ```
        # Config:
        - httpVersion: HTTP version; Don't change this unless you know what you are doing!
        - serverName: Server Name; This appears in the `Server` response header.
        - defaultOrigin: Origin Header Value; This value appears in the `Access-Control-Allow-Origin` request header.
        - maxHeaderKeyLength: Maximum header key length accepted before responding with `413 - Entity Too Large` error.
        - maxHeaderValueLength: Maximum header value length accepted before responding with `413 - Entity Too Large` error.
        - maxRecv: The set received size of bytes at which to stop blocking/listening over the socket and procced with proccessing the request. Default: `1024`. Too high of a value will cause connection-resets.
        - defaultResponse: The static response that is used if the default handler is the current handler.
        """
        for item in editParams:
            if item in defaults:
                defaults[item] = editParams[item]
            
    # UTILITY METHOD THAT SETS A CUSTOM HANDLER
    def set_handler(self, handler):
        """
        # Required format for custom handler:
        
        - Parameters
        ```
        myHandler(self, (str requestStatusLine, list requestHeaders, bytes requestBody,), (socket.socket clientConnection, tuple clientAddress,))
        ```
        ## OR SIMPLY:
        ```
        myHandler(self, REQUEST, CONNECTION)
        ```
        
        ---

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

            stdout.write('\nListening @ http://%s:%s ...' % self.vector)

            # START SERVER LOOP - MAKE THIS ASYNC!!!!!!
            while True:    

                # Wait for client connections
                client_connection, client_address = self.sock_.accept()

                # BOOL ERROR:
                error = False

                # Get the client request
                try:
                    request = client_connection.recv(defaults['maxRecv']).decode()
                except:
                    client_connection.close()
                    continue

                requestHeaders_buffer = request.split("\r\n")

                try:
                    requestBody = request.encode().split(b'\r\n\r\n')[1]
                except:
                    requestBody = b""
                    
                try:
                    requestStatusLine = requestHeaders_buffer.pop(0)
                except:
                    client_connection.close()
                    continue

                requestHeaders = []
                for unit in requestHeaders_buffer:
                    if unit != "" and ": " in unit:
                        key = unit.split(': ')[0]
                        value = unit.split(': ')[1]

                        # CHECK HEADER KEY/VALUE LENGTHS FOR EXTREMES
                        if len(key) > defaults['maxHeaderKeyLength'] or len(value) > defaults['maxHeaderValueLength']:
                            errorResponse(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, client_connection)
                            error = False
                        
                        else:
                            requestHeaders.append([key, value])

                # PROCESS REQUEST - SEND TO HANDLER
                # THINK OF ALL OF THESE PARAMETERS AS THE $_SERVER (PHP) VARIABLE

                # "otherAPI" accepts any left-overs when unpacking the 
                if not error:
                    # WE WONT ALLOW SENDING A RESPONSE FROM INSIDE THE HANDLERS AS IT COULD BREAK HTTP RULES OR CREATE NON-DETERMINISTIC ISSUES.
                    # INSTEAD, WE REQUIRE (responseStatusLine, responseHeaders, responseBody) TO BE RETURNED FOR FINAL PREPROCCESSING.

                    REQUEST = (requestStatusLine, requestHeaders, requestBody,)
                    CONNECTION = (client_connection, client_address,)

                    if self.handler is not None:
                        responseStatusLine, responseHeaders, responseBody, *otherAPI = self.handler(self, REQUEST, CONNECTION)

                    else:
                        responseStatusLine, responseHeaders, responseBody, *otherAPI = self.defaultHandler(self, REQUEST, CONNECTION)
                    
                    # ENSURE THAT ALL RESPONSE COMPONENTS ARE BYTES AND NOT STRING - 1
                    if type(responseStatusLine) != bytes and type(responseStatusLine) == str:
                        responseStatusLine = responseStatusLine.encode()

                    # ENSURE THAT ALL RESPONSE COMPONENTS ARE BYTES AND NOT STRING - 2
                    if type(responseBody) != bytes and type(responseBody) == str:
                        responseBody = responseBody.encode()    
                    
                    # ENSURE RESPONSE HEADERS ARE VALID
                    if type(responseHeaders) != list:
                        # TODO: RAISE A FATAL ERROR HERE!
                        return 
                
                    # SET CONTENT LENGTH HEADER IF RESPONSE BODY IS PRESENT
                    if len(responseBody):
                        responseHeaders.append(f'Content-Length: {str(len(responseBody))}')    

                    # ENCODE THE HEADERS
                    headersEncoded = ("\r\n".join(responseHeaders)).encode()    
                    
                    # ENCODE THE COMPLETE RESPONSE
                    response = responseStatusLine + headersEncoded + b"\r\n\r\n" + responseBody
                   
                    try:
                        # SEND THE RESPONSE
                        client_connection.sendall(response)

                        # CLOSE THE CLIENT'S SOCKET
                        client_connection.close()
                    except:
                        pass    


        # CREATES/STARTS THREAD
        t = Thread(target=thread)
        t.start()
        # APPEND NEW THREAD TO SERVER_THREADS; A UTILITY ARRAY FOR INTERACTING WITH MULTIPLE INSTANCES
        SERVER_THREADS.append(t)


