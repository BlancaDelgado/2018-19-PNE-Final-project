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
    if r.status == 400:
        return False

    else:
        txt_json = r.read().decode("utf-8")
        data = json.loads(txt_json)
        conn.close()
        return data


def error(error):
    """
    Select HTML file according to error.
    :param error: string with name of error (NoFile, Limit, NoSpecies).
    :return: contents to open.
    """

    if error == 'NoFile':
        msg_error = 'Sorry, this resource is not available.'

    elif error == 'Limit':
        msg_error = 'Make sure you introduce correct values. Limit must be a positive integer.'

    elif error == 'Species':
        msg_error = """
        This species is not available. 
        Check for valid species between parenthesis <a href="/listSpecies">here</a>."""

    else:
        msg_error = 'Unknown error. Try later please.'

    html = """<html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Error</title>
                    </head>
                    <body style="background-color: #F16E6C">
                        <br><br><br>
                        <h1>Oops...</h1>
                        <p>{msg_error}</p>
                        <br>
                        <a href="/">[Main page]</a>
                        <br><br>
                    </body>
                </html>""".format(msg_error=msg_error)
    return html


def info(title, data):
    """
    Creates HTMl page to show selected information.
    :param title: title for the web page created.
    :param data: info to be displayed in the web.
    :return: HTML contents.
    """

    html = """
        <html>
            <header>
                <meta charset="UTF-8">
                <title>Data</title>
            </header>
    
            <body>
                <h3><u>{TITLE}</u>:</h3>
                <p>{data}</p>
                <br>
                <a href="/">[Main page]</a>
                <br><br>
            </body>
            
        </html>
        """.format(TITLE=title, data=data)
    return html


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

        # --- 1.- LIST OF SPECIES
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

                    dname = i['display_name']
                    name = i['name']
                    list_species.append(str(n) + '. ' + dname + ' (<i>' + name + '</i>)')

                str_species = '<br>'.join(list_species)

                contents = info('SPECIES', str_species)

            except ValueError:  # unless limit is not valid
                contents = error('Limit')

        # --- 2.- KARYOTYPE
        elif 'karyotype' in self.path:

            path = self.path.split('?')
            species = path[1].split('=')[1]

            endpoint = '/info/assembly/' + species
            data = connect(endpoint)

            if 'error' in data.keys():  # wrong or no species selected
                contents = error('Species')
            else:
                karyotype = '<br>'.join(data['karyotype'])
                contents = info('KARYOTYPE', karyotype)

        # --- 3.- CHROMOSOME LENGTH
        elif 'chromosomeLength' in self.path:
            contents = 'CHROMOSOME'

        # Error
        else:
            contents = error('NoPage')

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
