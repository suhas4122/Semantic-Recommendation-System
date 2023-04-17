from sentence_transformers import SentenceTransformer
import numpy as np
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import os

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

def get_uri_data(uri):
    data = {}
    sparql.setQuery(sparql_prefix + """
        SELECT ?name ?price ?image ?link ?rating
        WHERE {
            """ + uri + """ rdfs:label ?name;
                            exs:price ?price;
                            exs:image ?image;
                            exs:link ?link;
                            exs:rating ?rating.
        }
    """)
    q = sparql.queryAndConvert()
    # print(q)
    data["name"] = q['results']['bindings'][0]['name']['value']
    data["price"] = q['results']['bindings'][0]['price']['value']
    data["image"] = q['results']['bindings'][0]['image']['value']
    data["link"] = q['results']['bindings'][0]['link']['value']
    data["rating"] = q['results']['bindings'][0]['rating']['value']
    return data

def get_cosine_similarity(embedding1, embedding2):
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))


def get_sim_score(uri, history_names):
    name = get_name_from_uri(uri)
    similarity_scores = []
    for history_name in history_names:
        embeddings = model.encode([name, history_name])
        similarity_scores.append(
            get_cosine_similarity(embeddings[0], embeddings[1]))
    similarity_scores.sort(reverse=True)
    top_len = int(len(similarity_scores) * 0.3)
    return sum(similarity_scores[:top_len]) / top_len

def string_matching_filter(all_product_uris, history_uris):
    history_names = [get_name_from_uri(uri) for uri in history_uris]
    result = []
    for uri in all_product_uris:
        avg_sim = get_sim_score(uri, history_names)
        if uri not in history_uris and avg_sim > 0.2:
            result.append((uri, avg_sim))
    return result


def common_purchase_filter(user_uri):
    sparql.setQuery(sparql_prefix + """
        SELECT ?product2 (COUNT(?user) AS ?count_user)
        WHERE {
            """ + user_uri + """ exs:bought ?product1.
            ?user exs:bought ?product1;
                  exs:bought ?product2.
            FILTER(?product1 != ?product2)
            FILTER(?user != """ + user_uri + """)
            FILTER NOT EXISTS {""" + user_uri + """ exs:bought ?product2.}
        } GROUP BY ?product2
        ORDER BY DESC (?count_user)
    """)
    ret = sparql.queryAndConvert()
    ret_val = ret['results']['bindings']
    result = [(x, int(y)) for x, y in zip([x['product2']['value']
                                           for x in ret_val], [y['count_user']['value'] for y in ret_val])]
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
        jaccard_similarity = len(set(cat).intersection(set(
            hist_categories[history_uri]))) / len(set(cat).union(set(hist_categories[history_uri])))
        similarities.append(jaccard_similarity)
    max_sim = max(similarities)
    return max_sim


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

    results = []
    for uri in all_product_uris:
        similarities = []
        for history_uri in history_uris:
            jaccard_similarity = len(set(categories[uri]).intersection(set(
                categories[history_uri]))) / len(set(categories[uri]).union(set(categories[history_uri])))
            similarities.append(jaccard_similarity)
        max_sim = max(similarities)
        if max_sim > 0.5 and max_sim <= 0.75:
            results.append((uri, max_sim))
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

    result_1 = string_matching_filter(all_products_uris, history_uris)
    result_2 = category_similarity_filter(all_products_uris, history_uris)

    df = pd.DataFrame(
        columns=['name_sim_score', 'cat_sim_score', 'rating', 'manuf_count'])
    for (uri, sc) in result_1:
        df.loc[uri, 'name_sim_score'] = sc
    for (uri, sc) in result_2:
        df.loc[uri, 'cat_sim_score'] = sc
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
        if np.isnan(df.loc[uri, 'name_sim_score']):
            df.loc[uri, 'name_sim_score'] = get_sim_score(uri, history_uris)
        if np.isnan(df.loc[uri, 'cat_sim_score']):
            df.loc[uri, 'cat_sim_score'] = cat_sim_score(uri, history_uris)
    return df

def prod_sim_score(uri_1, uri_2):
    name_1 = get_name_from_uri(uri_1)
    name_2 = get_name_from_uri(uri_2)
    embeddings = model.encode([name_1, name_2])
    return get_cosine_similarity(embeddings[0], embeddings[1])

def recommend(df):
    df['rec_score'] = (df['name_sim_score'] * 10 + df['cat_sim_score']
                       * 5 + df['rating'] * 1 + df['manuf_count'] * 1)
    df = df.sort_values(by=['rec_score'], ascending=False)

    recs = []
    i = 0
    while len(recs) < 10 and i < len(df.index):
        curr_uri = df.index[i]
        max_sim_1 = 0
        for uri in recs:
            max_sim_1 = max(max_sim_1, prod_sim_score(curr_uri, uri))
        max_sim_2 = 0
        for uri in history_uris:
            max_sim_2 = max(max_sim_2, prod_sim_score(curr_uri, uri))
        if max_sim_1 < 0.5 and max_sim_2 < 0.75:
            recs.append(curr_uri)
        i += 1
    return recs

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

for user_ind in range(1, 9):
    user_uri = "exr:user_" + str(user_ind)
    history_uris = get_history_uris()
    hist_categories = get_hist_categories()
    print("Started processing for user " + user_uri)

    if os.path.exists('df/df_' + str(user_ind) + '.csv'):
        df = pd.read_csv('df/df_' + str(user_ind) + '.csv', index_col=0)
    else:
        print("Calculating key metrics...")
        df = initial_filter(user_uri, history_uris)
        complete_df(df)
        df.replace('', 0, inplace=True)
        df.fillna(0, inplace=True)
        df = df.astype({'name_sim_score': 'float64', 'cat_sim_score': 'float64',
                    'rating': 'float64', 'manuf_count': 'int64'})
        df.to_csv('df/df_' + str(user_ind) + '.csv')

    if os.path.exists('results/recs_' + str(user_ind) + '.csv') is False:
        print("Getting recommendations...")
        recs = recommend(df)
        df_res = pd.DataFrame(columns=['uris'])
        df_res['uris'] = recs
        df_res.to_csv('results/recs_' + str(user_ind) + '.csv')

