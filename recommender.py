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

def common_purchase_filter(history_uris, user_uri):
    result = {}
    for uri in history_uris:
        sparql.setQuery("""
            prefix exs: <http://example.org/schema#> 
            prefix exr: <http://example.org/resource#>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT ?name 
            WHERE {
            """
                + uri + """ ^exs:bought/exs:bought ?product.
                FILTER(?product != """ + uri + """ )
                FILTER NOT EXISTS {?product ^exs:bought """ + user_uri + """ .}
                ?product rdfs:label ?name.
            }
        """)
        ret = sparql.queryAndConvert()
        for ret_val in ret['results']['bindings']:
            if ret_val['name']['value'] in result:
                result[ret_val['name']['value']] += 1
            else:
                result[ret_val['name']['value']] = 1
    return result

def category_similarity_filter(history_uris, all_product_uris):
    categories = {}
    for uri in all_product_uris:
        sparql.setQuery("""
            prefix exs: <http://example.org/schema#> 
            prefix exr: <http://example.org/resource#>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT ?categoryLabel 
            WHERE {
                """
            + uri + """ exs:category/rdf:rest*/rdf:first ?category.
                ?category rdfs:label ?categoryLabel.
            }
        """)
        ret = sparql.queryAndConvert()
        categories[uri] = []
        for ret_val in ret['results']['bindings']:
            categories[uri].append(ret_val['categoryLabel']['value'])
    # print(categories)
    
    results = []
    for uri in all_product_uris:
        similarities = []
        for history_uri in history_uris:
            # if uri == history_uri:
            jaccard_similarity = len(set(categories[uri]).intersection(set(categories[history_uri]))) / len(set(categories[uri]).union(set(categories[history_uri])))
            similarities.append(jaccard_similarity)
                # print(jaccard_similarity)
        if max(similarities) > 0.5 and max(similarities) != 1:
            results.append(uri)
    print(results)
    return results
    
def initial_filter(user_uri):
    history_uris = []
    sparql.setQuery("""
        prefix exs: <http://example.org/schema#> 
        prefix exr: <http://example.org/resource#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?uri
        WHERE {
        """
        + user_uri + """ exs:bought ?uri. 
        }
    """)
    for ret_val in sparql.queryAndConvert()['results']['bindings']:
        history_uris.append(ret_val['uri']['value'])
    
    all_products_uris = []
    sparql.setQuery("""
        prefix exs: <http://example.org/schema#> 
        prefix exr: <http://example.org/resource#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    
        SELECT ?uri
        WHERE {
            ?uri rdf:type exs:Product. 
        }
    """)
    for ret_val in sparql.queryAndConvert()['results']['bindings']:
        all_products_uris.append(ret_val['uri']['value'])
    
    print(len(history_uris), len(all_products_uris))
    
    file = open("data/uris.txt", "r")
    uris_check = file.read().splitlines()
    for uri in uris_check:
        if uri not in all_products_uris:
            print(uri)
    
    # result_1 = string_matching_fiter(history_uris, all_products_uris)
    # result_2 = category_similarity_filter(history_uris, all_products_uris)
    # result_3 = common_purchase_filter(history_uris, "exr:user_1")
    # return 

# result = 
initial_filter("exr:user_1")
# print(result.values(), len(result.values()))