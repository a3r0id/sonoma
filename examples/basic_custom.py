from sonoma import defaults, httpServer

server = httpServer('127.0.0.1', 8888)

defaults.defaultResponse = """ 
    <!DOCTYPE html><html><head>
    <style>html, body{ margin: 0 auto;text-align:center; }</style>
    </head><body>
    <h1 style=\"text-align:center;\">Hello World!</h1>
    <span>This is a modified version of the default webpage for %s.</span>
    </body></html>
    """ % defaults.serverName 

server.run()