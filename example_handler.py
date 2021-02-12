from sonoma import httpServer, defaults
from http import HTTPStatus

# DEFINE A CUSTOM HANDLER
def myHandler(self, requestStatusLine, requestHeaders, requestBody, client_connection, client_address):
    """
    ## Supported Methods:
    - GET
    - HEAD
    """

    print("Client: %s\n" % str(client_address))

    headerStrings = ["%s: %s\n" % (header[0], header[1]) for header in requestHeaders]

    myCustomResponse = """
        <!DOCTYPE html><html><head>
        <style>html, body{ margin: 0 auto;text-align:center; }</style>
        </head><body>
        <h1 style=\"text-align:center;\">Hello World!</h1>
        <span>This is a custom response from %s.</span>
        <br/><br/>
        <span>Request Headers:</span>
        <br/>
        <textarea cols="100" rows="100" style="width: 75%%;height: 100%%;margin: 0 auto;">%s</textarea>
        </body></html>
    """ % (defaults.serverName, "".join(headerStrings)) 
    
    # SERVE GET
    if requestStatusLine.split()[0].lower() == "get":
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.OK, contentType="html")
        responseBody = myCustomResponse
        return (responseStatusLine, responseHeaders, responseBody)

    # SERVE HEAD
    elif requestStatusLine.split()[0].lower() == "head":   
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.OK, contentType="text")
        return (responseStatusLine, responseHeaders, "")  
    
    # RESPOND WITH 405 STATUS - METHOD NOT ALLOWED
    else:
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.METHOD_NOT_ALLOWED, contentType="text")
        return (responseStatusLine, responseHeaders, "")   


# INITIALIZE THE SERVER BUT SET OUR CUSTOM HANDLER BEFORE RUNNING.
server = httpServer('127.0.0.1', 8888)

server.set_handler(myHandler)

server.run()