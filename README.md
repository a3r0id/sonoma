# Sonoma
[![PyPI version](https://badge.fury.io/py/sonoma.svg)](https://badge.fury.io/py/sonoma)

A tiny, programmable http-server crafting- framework that is built with security and simplicity in mind.

----

![](https://imengine.prod.srp.navigacloud.com/?uuid=C31C28DA-402C-4C02-9083-6C8DACCF1556&type=primary&q=72&width=1024)

----

# Setup
```pip install sonoma```


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

# Advanced Usage: Default Handler

### Server
```python
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

    headerStrings = []
    for header in requestHeaders:
        headerStrings.append("%s: %s\n" % (header[0], header[1]))   

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
```

### Browser
![](https://cdn.discordapp.com/attachments/796917179987656774/809904244387348490/unknown.png)


# Conclusion

- Adding better documentation soon!
