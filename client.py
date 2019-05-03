# Blanca Delgado; client advanced level
# Client for testing json files of the server

import http.client
import termcolor
import itertools
import json

port = 8000
server = '127.0.0.1'

print('TRYING MY SERVER:\n\n')

termcolor.cprint("Connecting to server: {s} (PORT {p})".format(s=server, p=port), 'green')
conn = http.client.HTTPConnection(server, port)

titles = [
    'ALL SPECIES'
    'SOME SPECIES'
    'KARYOTYPE'
    'CHROMOSOME LENGTH'
    'GENE SEQUENCE'
    'GENE INFORMATION'
    'GENE CALCULATIONS'
    'ALL GENES'
]

# Change this endpoints to try other possibilities
endpoints = [
    '/listSpecies?json=1'
    '/listSpecies?limit=3&json=1'
    '/karyotype?specie=homo_sapiens&json=1'
    '/chromosomeLength?specie=homo_sapiens&chromo=7&json=1'
    '/geneSeq?gene=FRAT1&json=1'
    '/geneInfo?gene=FRAT1&json=1'
    '/geneCalc?gene=FRAT1&json=1'
    '/geneList?chromo=7&start=30000&end=35000&json=1'
]

for title, endpoint in zip(titles, endpoints):

    # Connect to specific endpoint
    conn.request('GET', endpoint)
    r = conn.getresponse()
    termcolor.cprint("Response received: {s} {r}".format(s=r.status, r=r.reason))

    data = r.read().decode("utf-8")
    response = json.loads(data)

    print()
    print(title)

    print()
    print(response)
