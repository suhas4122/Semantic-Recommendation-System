from sentence_transformers import SentenceTransformer
import numpy as np
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from functools import lru_cache

sparql = SPARQLWrapper("http://localhost:3030/all_products/query")
sparql.setReturnFormat(JSON)

sparql_prefix = """
    prefix exs: <http://example.org/schema#>
    prefix exr: <http://example.org/resource#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
"""


def get_name_from_uri(uri):
    sparql.setQuery(sparql_prefix + """
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


def get_sim_score(uri, history_names):
    name = get_name_from_uri(uri)
    similarity_scores = []
    for history_name in history_names:
        embeddings = model.encode([name, history_name])
        similarity_scores.append(
            get_cosine_similarity(embeddings[0], embeddings[1]))
    return sum(similarity_scores) / len(similarity_scores)

# @lru_cache(maxsize=1000)
def string_matching_filter(all_product_uris, history_uris):
    history_names = [get_name_from_uri(uri) for uri in history_uris]
    result = []
    for uri in all_product_uris:
        avg_sim = get_sim_score(uri, history_names)
        if uri not in history_uris and avg_sim > 0.2:
            result.append((uri, avg_sim))
    return result


def common_purchase_filter(user_uri, history_uris):
    result = {}
    for uri in history_uris:
        sparql.setQuery(sparql_prefix + """
            SELECT ?product
            WHERE {
            """
                        + uri + """ ^exs:bought/exs:bought ?product.
                FILTER(?product != """ + uri + """ )
                FILTER NOT EXISTS {?product ^exs:bought """ + user_uri + """ .}
            }
        """)
        ret = sparql.queryAndConvert()
        for ret_val in ret['results']['bindings']:
            if ret_val['product']['value'] in result:
                result[ret_val['product']['value']] += 1
            else:
                result[ret_val['product']['value']] = 1
    result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    return result


def cat_sim_score(uri, history_uris):
    cat = []
    sparql.setQuery(sparql_prefix + """
        SELECT ?categoryLabel
        WHERE {
            """
                    + uri + """ exs:category/rdf:rest*/rdf:first ?category.
            ?category rdfs:label ?categoryLabel.
        }
    """)
    ret = sparql.queryAndConvert()
    for ret_val in ret['results']['bindings']:
        cat.append(ret_val['categoryLabel']['value'])
    similarities = []
    for history_uri in history_uris:
        # if uri == history_uri:
        jaccard_similarity = len(set(cat).intersection(set(
            hist_categories[history_uri]))) / len(set(cat).union(set(hist_categories[history_uri])))
        similarities.append(jaccard_similarity)
        # print(jaccard_similarity)
    max_sim = max(similarities)

def get_history_uris():
    history_uris = []
    sparql.setQuery(sparql_prefix + """
        SELECT ?uri
        WHERE {
        """
                    + user_uri + """ exs:bought ?uri. 
        }
    """)
    for ret_val in sparql.queryAndConvert()['results']['bindings']:
        history_uris.append("exr:" + ret_val['uri']['value'].split('#')[1])
    return history_uris

def get_hist_categories():
    hist_categories = {}
    for uri in history_uris:
        sparql.setQuery(sparql_prefix + """
            SELECT ?categoryLabel 
            WHERE {
                """
                        + uri + """ exs:category/rdf:rest*/rdf:first ?category.
                ?category rdfs:label ?categoryLabel.
            }
        """)
        ret = sparql.queryAndConvert()
        hist_categories[uri] = []
        for ret_val in ret['results']['bindings']:
            hist_categories[uri].append(ret_val['categoryLabel']['value'])
    return hist_categories


def category_similarity_filter(all_product_uris, history_uris):
    categories = {}
    for uri in all_product_uris:
        sparql.setQuery(sparql_prefix + """
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
            jaccard_similarity = len(set(categories[uri]).intersection(set(
                categories[history_uri]))) / len(set(categories[uri]).union(set(categories[history_uri])))
            similarities.append(jaccard_similarity)
            # print(jaccard_similarity)
        max_sim = max(similarities)
        if max_sim > 0.5 and max_sim <= 0.75:
            results.append((uri, max_sim))
    # print(results)
    return results


def initial_filter(user_uri, history_uris):
    all_products_uris = []
    sparql.setQuery(sparql_prefix + """
        SELECT ?uri
        WHERE {
            ?uri rdf:type exr:Product. 
        }
    """)
    for ret_val in sparql.queryAndConvert()['results']['bindings']:
        all_products_uris.append(
            "exr:" + ret_val['uri']['value'].split('#')[1])

    # print(all_products_uris, history_uris)
    result_1 = string_matching_filter(all_products_uris, history_uris)
    result_2 = category_similarity_filter(all_products_uris, history_uris)

    # name similarity score, category similarity score, rating, how many products of this manufacturer are in the history
    # create pd dataframe with named index of uri
    df = pd.DataFrame(
        columns=['name_sim_score', 'cat_sim_score', 'rating', 'manuf_count'])
    # print(result_1)
    for (uri, sc) in result_1:
        df.loc[uri, 'name_sim_score'] = sc
    for (uri, sc) in result_2:
        df.loc[uri, 'cat_sim_score'] = sc
    print(df)
    return df


def get_rating(uri):
    sparql.setQuery(sparql_prefix + """
        SELECT ?rating
        WHERE {
        """
                    + uri + """ exs:rating ?rating. 
        }
    """)
    ret = sparql.queryAndConvert()
    rating = ret['results']['bindings'][0]['rating']['value']
    return rating


def get_manufacturer_count(uri, user):
    sparql.setQuery(sparql_prefix + """
        SELECT DISTINCT(?uri)
        WHERE {
        """
            + uri + """ exs:manufacturer ?manufacturer. """
            + user + """ exs:bought ?uri. 
            ?uri exs:manufacturer ?manufacturer.
        }
    """)
    ret = sparql.queryAndConvert()
    return len(ret['results']['bindings'])


def complete_df(df):
    for uri in df.index:
        df.loc[uri, 'rating'] = get_rating(uri)
        df.loc[uri, 'manuf_count'] = get_manufacturer_count(uri, user_uri)
        # check if it is Nan
        if np.isnan(df.loc[uri, 'name_sim_score']):
            df.loc[uri, 'name_sim_score'] = get_sim_score(uri, history_uris)
        if np.isnan(df.loc[uri, 'cat_sim_score']):
            df.loc[uri, 'cat_sim_score'] = cat_sim_score(uri, history_uris)
    return df


# common_purchases = common_purchase_filter(history_uris, user_uri)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
user_uri = "exr:user_1"
history_uris = get_history_uris()
hist_categories = get_hist_categories()
df = initial_filter(user_uri, history_uris)
complete_df(df)
print(df)