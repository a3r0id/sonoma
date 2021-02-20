from sonoma import httpServer, HTTPStatus, sonomaPrint, serverGmtTime
from json import dumps
from urllib.parse import urlparse, parse_qs

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
    
    # SERVE GET-JSON
    if requestStatusLine.split()[0].lower() == "get":

        # GET OUR JSON HEADERS + STATUS LINE
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.OK, contentType="json")
        
        # PARSE THE GET QUERY
        try:
            clientQuery = parse_qs(urlparse(requestStatusLine.split()[1]).query)
        except:
            # IF QUERY CANNOT BE PARSED THEN RESPOND WITH AN ERROR MESSAGE
            return (responseStatusLine, responseHeaders, dumps({'error': 'Invalid url query!'}))

        # GET TIME FOR ONE OF OUR SERVERSIDE PROCESSING EXAMPLES
        tstamp = serverGmtTime()

        responseBody = dumps({
            'query': clientQuery,
            'time_gmt': tstamp
            }, indent=4)
            
        return (responseStatusLine, responseHeaders, responseBody)
    
    # RESPOND WITH 405 STATUS - METHOD NOT ALLOWED
    else:
        responseStatusLine, responseHeaders = self.httpHeaders(HTTPStatus.METHOD_NOT_ALLOWED, contentType="text")
        return (responseStatusLine, responseHeaders, "")   

# INITIALIZE THE SERVER BUT SET OUR CUSTOM HANDLER BEFORE RUNNING.
server = httpServer('127.0.0.1', 8888)

server.set_handler(myHandler)

server.run()