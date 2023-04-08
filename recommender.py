from sentence_transformers import SentenceTransformer
import numpy as np
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://localhost:3030/all_products/query")
sparql.setReturnFormat(JSON)

def get_name_from_uri(uri):
    sparql.setQuery("""
        prefix exs: <http://example.org/schema#> 
        prefix exr: <http://example.org/resource#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT ?name 
        WHERE {
        """
        + uri + 
        """ rdfs:label ?name .
        }
    """)
    ret = sparql.queryAndConvert()
    name = ret['results']['bindings'][0]['name']['value']
    return name

def get_cosine_similarity(embedding1, embedding2):
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))    
    
def string_matching_fiter(history_uris, all_product_uris):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    history_names = [get_name_from_uri(uri) for uri in history_uris]
    result = []
    for uri in all_product_uris:
        name = get_name_from_uri(uri)
        similarity_scores = []
        for history_name in history_names:
            embeddings = model.encode([name, history_name])
            similarity_scores.append(get_cosine_similarity(embeddings[0], embeddings[1]))
        if uri not in history_uris and max(similarity_scores) > 0.5:
            result.append(uri)
    return result
                

def initial_filter(history_file_name, all_product_file_name):
    history_file = open(history_file_name, 'r')
    history_uris = []
    for line in history_file:
        history_uris.append(line.strip())
    all_products_file = open(all_product_file_name, 'r')
    all_products_uris = []
    for line in all_products_file:
        all_products_uris.append(line.strip())  
    result_1 = string_matching_fiter(history_uris, all_products_uris)
    return result_1

result = initial_filter('user_history.txt', 'uris.txt')
for uri in result:
    print(get_name_from_uri(uri))