from sonoma import httpServer, defaults, sonomaPrint
from sonoma import setCookie, parseCookies
from http import HTTPStatus


# DEFINES CUSTOM HANDLER
def myHandler(self, REQUEST, CONNECTION):
    """
    ## Supported Methods:
    - GET
    - HEAD
    """

    # UNPACK "REQUEST" TUPLE 
    requestStatusLine, requestHeaders, requestBody = REQUEST

    # UNPACK CONNECTION TUPLE
    client_connection, client_address = CONNECTION

    # LOG THE REQUEST TO STDOUT
    sonomaPrint("%s -> %s Request: %s" % (str(self.vector), str(client_address), str(requestStatusLine),))
    
    #
    # RESOLVE THE REQUEST METHOD AND RESPOND ACCORDINGLY:
    #
    
    # SERVE GET
    if requestStatusLine.split()[0].lower() == "get":

        # GET OUR DEFAULT HEADERS + STATUS LINE
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.OK, contentType="html")
        

        # CREATE A LIST OF STRINGS OF EACH REQUEST HEADER FOR USE IN OUR EXAMPLE
        headerStrings = ["%s: %s\n" % (header[0], header[1]) for header in requestHeaders]


        # HERES HOW WE CAN WORK WITH COOKIES, BOTH REQUEST AND RESPONSE:
        requestCookies = parseCookies(requestHeaders) # GET REQUEST COOKIES
        #sonomaPrint(requestCookies)        
        
        setCookie(responseHeaders, "cookieName", "cookieValue", ['Secure', 'HttpOnly']) # SET A RESPONSE COOKIE
        #sonomaPrint(responseHeaders)


        # CREATE A CUSTOM RESPONSE
        responseBody = ("""
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
        """ % (defaults['serverName'], "".join(headerStrings))).encode() 
            
        return (responseStatusLine, responseHeaders, responseBody)
    
    # RESPOND WITH 405 STATUS - METHOD NOT ALLOWED
    else:
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.METHOD_NOT_ALLOWED, contentType="text")
        return (responseStatusLine, responseHeaders, "")   

# INITIALIZE THE SERVER BUT SET OUR CUSTOM HANDLER BEFORE RUNNING.
server = httpServer('127.0.0.1', 8888)

server.set_handler(myHandler)

server.run()