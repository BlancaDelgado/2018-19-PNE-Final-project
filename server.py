# Web server basic level

import http.server
import http.client
import socketserver
import termcolor
import json


# Protocol: HTTP
# Response: HTML page


# BASIC LEVEL

def connect(ENDPOINT):
    """
    Client that connects to ENSEMBL.
    :param ENDPOINT: request to obtain desired info.
    :return: json file downloaded from GITHUB.
    """

    HOSTNAME = "http://rest.ensembl.org"
    METHOD = "GET"
    headers = {'User-Agent': 'http-client', 'Content-Type': 'application/json'}

    # CONNECT
    termcolor.cprint('\nConnecting: ' + HOSTNAME + ENDPOINT, 'green')
    conn = http.client.HTTPSConnection(HOSTNAME)
    conn.request(METHOD, ENDPOINT, None, headers)
    r = conn.getresponse()

    # POLISH INFO
    termcolor.cprint('Response received: {num} {OK}'.format(num=r.status, OK=r.reason), 'green')
    txt_json = r.read().decode("utf-8")
    conn.close()

    data = json.loads(txt_json)
    return data


class MainHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        # PRINT REQUEST LINE
        termcolor.cprint(self.requestline, 'green')

        # READ FILE DEPENDING ON PATH
        # Main page
        if self.path == '/' or 'favicon' in self.path:
            f200 = open('main.html', 'r')
            contents = f200.read()

        # Error
        else:
            f0 = open('error_NoPage.html', 'r')
            contents = f0.read()

        # GET RESPONSE MESSAGE
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(str.encode(contents)))
        self.end_headers()

        self.wfile.write(str.encode(contents))


# -- Main program
PORT = 8000

with socketserver.TCPServer(('', PORT), MainHandler) as httpd:
    httpd.allow_reuse_address = True
    print('Serving at PORT: {}'.format(PORT))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('EXIT BY USER.')
        httpd.server_close()

# /listSpecies --- all names of species, OPTIONAL 'limit' for max number
# /karyotype --- karyotype of an 'specie'
# /chromosomeLength --- length of the chromosome ('chromo') of a given 'specie'
# / --- main endpoint, HTML with forms to access all previous services

# ELSE --- error page
