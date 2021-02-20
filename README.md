# Sonoma
[![PyPI version](https://badge.fury.io/py/sonoma.svg)](https://badge.fury.io/py/sonoma)

A tiny, low-level, programmable http-server-crafting framework that is built with security and simplicity in mind.

----

![](https://imengine.prod.srp.navigacloud.com/?uuid=C31C28DA-402C-4C02-9083-6C8DACCF1556&type=primary&q=72&width=1024)

----

# Setup
```pip install sonoma```

----


# Basic Usage

### Server
```python
from sonoma import httpServer

server = httpServer('127.0.0.1', 8888)

server.run()
```

### Browser
```
                Hello World!
This is the default webpage for Sonoma/1.0.x.
```

----

# Basic Usage: Custom Response
### Server
```python
from sonoma import defaults, httpServer

server = httpServer('127.0.0.1', 8888)

defaults['defaultResponse'] = """ 
    <!DOCTYPE html><html><head>
    <style>html, body{ margin: 0 auto;text-align:center; }</style>
    </head><body>
    <h1 style=\"text-align:center;\">Hello World!</h1>
    <span>This is a modified version of the default webpage for %s.</span>
    </body></html>
    """ % defaults['serverName'] 

server.run()
```

### Browser
```
                        Hello World!
This is a modified version of the default webpage for Sonoma/1.0.12.
```

----

# Advanced Usage: Custom Handler
### Server
```python
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
```

### Browser
![](https://cdn.discordapp.com/attachments/796917179987656774/809904244387348490/unknown.png)

----

# Advanced Handler: JSON API
### Server
```python
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
```
### Browser
> http://127.0.0.1:8888/?testQuery=1
```json
{
    "query": {
        "testQuery": [
            "1"
        ]
    },
    "time_gmt": "Sat, 20 Feb 2021 20:18:51 GMT"
}
```
# Conclusion

- Adding better documentation soon!
