import random
import os
from SPARQLWrapper import SPARQLWrapper, JSON

# read uris.txt file and create a list of uris
uris = []
uris_file = open(file='data/uris.txt', mode='r')
for line in uris_file:
    # append the uri to the list without the newline character
    uris.append(line[:-1])

# create manufacturer to list of products dictionary using sparql

sparql = SPARQLWrapper("http://localhost:3030/all_products/query")
sparql.setReturnFormat(JSON)

sparql_prefix = """
    prefix exs: <http://example.org/schema#>
    prefix exr: <http://example.org/resource#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
"""

def get_multi_manufs():
    manufacturer_to_products = {}
    for uri in uris:
        sparql.setQuery(sparql_prefix + """
            SELECT ?manufacturer
            WHERE {
            """
                    + uri +
                    """ exs:manufacturer ?manufacturer .
            }
        """)
        ret = sparql.queryAndConvert()
        manufacturer = ret['results']['bindings'][0]['manufacturer']['value']
        if manufacturer in manufacturer_to_products:
            manufacturer_to_products[manufacturer].append(uri)
        else:
            manufacturer_to_products[manufacturer] = [uri]

    random_uris = []
    multi_manufs = []
    for manufacturer in manufacturer_to_products:
        if len(manufacturer_to_products[manufacturer]) > 1:
            multi_manufs.append(manufacturer.split('#')[1])
            random_uris.extend(random.choice(manufacturer_to_products[manufacturer]))

    with open('data/multi_manufs.txt', 'w') as f:
        for line in multi_manufs:
            f.write(f"{line}\n")

# randomly select 100 uris from the list
random_uris = random.sample(uris, 100)

# # create directory to store user history files
# if not os.path.exists('user_history_files'):
#     os.mkdir('user_history_files')

# create a user_histories.txt file
user_histories_file = open(file='data/user_histories.ttl', mode='w')

# make 8 user_history_files, each containing 10 uris randomly selected from the list
for j in range(8):
    user_histories_file.write('exr:user_' + str(j + 1) + '\n')
    user_histories_file.write('\trdf:type exr:User ;\n')
    # select randomly 10 uris from the random_uris list for each user
    user_uris = random.sample(random_uris, 10)  
    for i in range(10):
        user_histories_file.write('\texs:bought ' + user_uris[i])
        if i != len(user_uris) - 1:
            user_histories_file.write(' ;\n')
        else:
            user_histories_file.write(' .\n\n')

# get_multi_manufs()