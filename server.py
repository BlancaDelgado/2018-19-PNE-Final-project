# Web server basic level

import http.server
import http.client
import socketserver
import termcolor

import json
import requests
import sys


# Protocol: HTTP
# Response: HTML page


# BASIC LEVEL

def connect(ENDPOINT):
    """
    Client that connects to ENSEMBL.
    :param ENDPOINT: request to obtain desired info.
    :return: json file downloaded from GITHUB.
    """

    HOSTNAME = "rest.ensembl.org"
    METHOD = 'GET'
    headers = {'content-type': 'application/json'}

    # CONNECT
    termcolor.cprint('Connecting: http://' + HOSTNAME + ENDPOINT, 'green')
    conn = http.client.HTTPConnection(HOSTNAME)
    conn.request(METHOD, ENDPOINT, '?', headers)
    r = conn.getresponse()

    # POLISH INFO
    termcolor.cprint('Response received: {num} {OK}'.format(num=r.status, OK=r.reason), 'green')
    txt_json = r.read().decode("utf-8")
    data = json.loads(txt_json)
    conn.close()
    return data


class MainHandler(http.server.BaseHTTPRequestHandler):

    socketserver.TCPServer.allow_reuse_address = True

    def do_GET(self):

        # PRINT REQUEST LINE
        termcolor.cprint('\n'+self.requestline, 'green')

        # READ FILE DEPENDING ON PATH
        # Main page
        if self.path == '/' or 'favicon' in self.path:
            f200 = open('main.html', 'r')
            contents = f200.read()

        # GET: list of species
        elif 'listSpecies' in self.path:

            endpoint = '/info/species'
            data = connect(endpoint)['species']

            try:  # set limit, find species
                if '=' in self.path:
                    path = self.path.split('?')
                    limit = path[1].split('=')[1]
                    limit = int(limit)
                else:
                    limit = len(data)

                list_species = []
                n = 0
                for i in data:
                    n += 1
                    if n > limit:
                        break  # limit reached

                    name = i['display_name']
                    list_species.append(str(n) + '. ' + name)

                str_species = '<br>'.join(list_species)

                contents = """
                <html>
                    <header>
                        <meta charset="UTF-8">
                        <title>Species</title>
                    </header>
                    
                    <body>
                        <h3><u>SPECIES</u>:</h3>
                        <p>{species}</p>
                        <br>
                        <a href="/">[Main page]</a>
                        <br><br>
                    </body>
                </html>
                
                """.format(species=str_species)

            except ValueError:  # unless limit is not valid
                f02 = open('error_ValueError.html', 'r')
                contents = f02.read()

        # GET: karyotype
        elif 'karyotype' in self.path:
            contents = 'KARYOTYPE'

        # GET: chromosome length
        elif 'chromosomeLength' in self.path:
            contents = 'CHROMOSOME'

        # Error
        else:
            f01 = open('error_NoPage.html', 'r')
            contents = f01.read()

        # GET RESPONSE MESSAGE
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(str.encode(contents)))
        self.end_headers()

        self.wfile.write(str.encode(contents))


# -- Main program
PORT = 8000

with socketserver.TCPServer(('', PORT), MainHandler) as httpd:
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
