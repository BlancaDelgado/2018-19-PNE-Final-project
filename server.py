# Blanca Delgado; web server advanced level

import http.server, http.client, socketserver
import termcolor
import json


# FUNCTIONS TO WORKOUT PROGRAM:
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


# FUNCTIONS TO GET HTML CONTENTS:
def error(error, species=None):
    """
    Select HTML file according to error.
    :param error: string with name of error (NoFile, Limit, NoSpecies).
    :return: contents to open.
    """

    if error == 'NoFile':
        msg_error = 'Sorry, this resource is not available.'

    elif error == 'Limit':
        msg_error = 'Make sure to introduce correct values. Limit must be a positive integer.'

    elif error == 'Species':
        msg_error = """
        This species is not available. 
        Check for valid species between parenthesis <a href="/listSpecies">here</a>."""

    elif error == 'NoSpecies':
        msg_error = 'Make sure to introduce correct values. A species must be selected!'

    elif error == 'NoChromo':
        msg_error = """
        This chromosome could not be found in the karyotype of '{species}'.<br>
        Check for valid chromosomes <a href="/karyotype?specie={species}">here</a>.""".format(species=species)

    elif error == 'WrongChromo':
        msg_error = """
        We could not analyze your operation.
        Please try another chromosome in the karyotype of '{species}' or try different lengths!<br>
        Check for valid chromosomes <a href="/karyotype?specie={species}">here</a>.""".format(species=species)

    elif error == 'NoGene':
        msg_error = 'This gene is not available.'

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


# FUNCTIONS TO WORKOUT ENDPOINTS:
def get_gene(gene):
    """
    Returns ID of gene from Ensembl.
    :param gene: name of a human gene.
    :return:    String with ID of gene if it exists.
                False if gene could not be found.
    """
    endpoint = '/homology/symbol/human/' + gene
    data = connect(endpoint)

    if not bool(data):
        ID = ''

    else:
        ID = data['data'][0]['id']
    return ID


class MainHandler(http.server.BaseHTTPRequestHandler):

    socketserver.TCPServer.allow_reuse_address = True

    def do_GET(self):

        # PRINT REQUEST LINE
        termcolor.cprint('\n'+self.requestline, 'green')

        # READ FILE DEPENDING ON PATH

        # Declare variables to avoid problems
        num_q_paths, num_a_paths, num_paths, restapi = None, None, None, None
        path_0, path_1, path_2, path_3 = None, None, None, None

        # First check most common error and organize info
        contents = error('NoFile')  # avoid non-mentioned variables in case of error

        num_slash = self.path.count('/')
        if num_slash != 1:
            contents = error('NoFile')

        else:  # save all parts of the path in different variables
            num_q_paths = self.path.count('?')
            num_a_paths = self.path.count('&')
            num_paths = num_q_paths + num_a_paths

            if num_paths != 0:
                path = self.path.split('?')[1]
                path = path.split('&')

                if num_paths >= 1:

                    if path[0].split('=')[0] != 'json':
                        path_1 = path[0].split('=')[1]

                    if num_paths >= 2:

                        if path[1].split('=')[0] != 'json':
                            path_2 = path[1].split('=')[1]

                        if num_paths >= 3:
                            if path[2].split('=')[0] != 'json':
                                path_3 = path[2].split('=')[1]

            # Check if JSON is requested
            if 'json' in self.path:
                restapi = True
            else:
                restapi = False

        # --- 0.0.- MAIN PAGE
        if self.path == '/' or 'favicon' in self.path:
            f200 = open('main.html', 'r')
            contents = f200.read()

        # --- 1.1.- LIST OF SPECIES
        elif 'listSpecies' in self.path:
            endpoint = '/info/species'
            data = connect(endpoint)['species']

            try:  # set limit, find species
                if (num_paths == 1 and restapi == False) or (num_paths == 2 and restapi == True):
                    limit = int(path_1)
                else:
                    limit = len(data)

                list_species = []
                json_species = []
                n = 0
                for i in data:
                    n += 1
                    if n > limit:
                        break  # limit reached

                    dname = i['display_name']
                    name = i['name']
                    list_species.append(str(n) + '. ' + dname + ' (<i>' + name + '</i>)')
                    json_species.append([{'display_name':dname, 'name':name}])

                str_species = '<br>'.join(list_species)

                if restapi:
                    contents = json.dumps(json_species)

                else:
                    contents = info('SPECIES', str_species)

            except ValueError:  # unless limit is not valid
                contents = error('Limit')

        # --- 1.2.- KARYOTYPE
        elif 'karyotype' in self.path:
            species = path_1
            endpoint = '/info/assembly/' + species
            data = connect(endpoint)

            try:
                if bool(data):
                    karyotype = '<br>'.join(data['karyotype'])
                    json_karyotype = data['karyotype']

                    if restapi:
                        contents = json.dumps({'karyotype': json_karyotype})
                    else:
                        contents = info('KARYOTYPE', karyotype)

                else:  # wrong species selected, warning dict received
                    contents = error('Species')

            except KeyError:  # no species selected, no dict received
                contents = error('NoSpecies')

        # --- 1.3.- CHROMOSOME LENGTH
        elif 'chromosomeLength' in self.path:
            species = path_1
            chromo = path_2
            endpoint = '/info/assembly/' + species
            data = connect(endpoint)

            try:
                if bool(data):

                    top_data = data['top_level_region']

                    ok_chromo = False
                    for i in top_data:
                        if i['coord_system'] == 'chromosome' and i['name'] == chromo:
                            ok_chromo = True
                            length = str(i['length'])
                            chromosomes = 'Length of chromosome (' + chromo + '): ' + length

                            if restapi:
                                contents = json.dumps({'length': length})
                            else:
                                contents = info('CHROMOSOME', chromosomes)

                    if not ok_chromo:  # not valid chromosome
                        contents = error('NoChromo', species=species)

                else:  # wrong species selected, warning dict received
                    contents = error('Species')

            except KeyError:  # no species selected, no dict received
                contents = error('NoSpecies')

        # --- 2.1.- SEQUENCE OF A GENE
        elif 'geneSeq' in self.path:
            gene = path_1
            gene_ID = get_gene(gene)

            if not bool(gene_ID):
                contents = error('NoGene')
            else:
                endpoint = '/sequence/id/' + gene_ID
                data = connect(endpoint)
                seq = data['seq']

                if restapi:
                    contents = json.dumps({'sequence': seq})
                else:
                    msg_seq = []
                    i = 0
                    for nucleotide in seq:
                        msg_seq.append(nucleotide)
                        i += 1
                        if i > 90:
                            msg_seq.append('<br>')
                            i = 0

                    msg_seq = "".join(msg_seq)
                    title = (gene + ' SEQUENCE').upper()
                    contents = info(title, msg_seq)

        # --- 2.2.- INFORMATION OF THE GENE
        elif 'geneInfo' in self.path:
            gene = path_1
            gene_ID = get_gene(gene)

            if not bool(gene_ID):
                contents = error('NoGene')
            else:
                endpoint = '/sequence/id/' + gene_ID

                data = connect(endpoint)['desc']
                data = data.split(':')

                i_chrome = str(data[1]) + '.p' + str(data[2])
                i_start = str(data[3])
                i_end = str(data[4])
                i_length = str(int(data[4]) - int(data[3]))
                i_id = gene_ID

                if restapi:
                    i_all = {'chromosome': i_chrome, 'id': i_id, 'start': i_start, 'end': i_end, 'length': i_length}
                    contents = json.dumps(i_all)
                else:
                    html_chrome = 'CHROMOSOME: ' + i_chrome
                    html_start = '<br>START: ' + i_start
                    html_end = 'END: ' + i_end
                    html_length = 'LENGTH: ' + i_length
                    html_id = 'ID: ' + i_id

                    i_all = [html_chrome, html_id, html_start, html_end, html_length]
                    i_all = '<br>'.join(i_all)
                    contents = info('INFORMATION', i_all)

        # --- 2.3.- CALCULATIONS OF THE GENE
        elif 'geneCalc' in self.path:
            gene = path_1
            gene_ID = get_gene(gene)

            if not bool(gene_ID):
                contents = error('NoGene')
            else:
                endpoint = '/sequence/id/' + gene_ID
                data = connect(endpoint)
                seq = data['seq']

                c_all = []
                c_json = {}

                c_length = str(len(seq))
                html_c_length = 'LENGTH: ' + c_length

                c_json['total_length'] = c_length
                c_all.append(html_c_length)

                for i in 'ACGT':
                    num = str(seq.count(i))
                    try:
                        c_perc = round((int(num) / len(seq)) * 100, 2)
                        html_perc = '{}%'.format(c_perc)
                    except ZeroDivisionError:
                        c_perc = 0
                        html_perc = '0%'

                    i_calc = i + ': ' + num + ' (' + html_perc + ')'
                    c_all.append(i_calc)

                    c_json[i] = {'count': num, 'percentage': c_perc}

                c_all = '<br>'.join(c_all)

                if restapi:
                    contents = json.dumps(c_json)
                else:
                    contents = info('CALCULATIONS', c_all)

        # --- 2.4.- NAMES OF GENES IN A CHROMOSOME
        elif 'geneList' in self.path:
            l_chromo = path_1
            l_start = path_2
            l_end = path_3
            endpoint = '/overlap/region/human/' + l_chromo + ':' + l_start + '-' + l_end + '?feature=gene'
            data = connect(endpoint)

            if not bool(data):
                contents = error('WrongChromo', 'homo_sapiens')
            else:
                genes = []
                for i in data:
                    l_gene = i['external_name']
                    genes.append(l_gene)
                html_genes = '<br>'.join(genes)

                if restapi:
                    contents = json.dumps({'genes': genes})
                else:
                    contents = info('GENES LOCATED IN THE CHROMOSOME', html_genes)

        # GET RESPONSE MESSAGE
        self.send_response(200)

        if restapi:
            self.send_header('Content-Type', 'application/json')
        else:
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
