import streamlit as st
from helper import *
import json
        
st.set_page_config(
    page_title="Semantic Recommender System",
    page_icon="🎈",
    layout="wide"
)

st.title("Semantic Recommender System")
cc1, pad1, cc2, pad2, cc3 = st.columns([10, 2, 10, 2, 10])

def get_uri_data(uri):
    data = {}
    sparql.setQuery(sparql_prefix + """
        SELECT ?name ?price ?image ?rating
        WHERE {
            """ + uri + """ rdfs:label ?name;
                            exs:price ?price;
                            exs:image ?image;
                            exs:rating ?rating.
        }
    """)
    data["name"] = sparql.queryAndConvert()['results']['bindings'][0]['name']['value']
    data["price"] = sparql.queryAndConvert()['results']['bindings'][0]['price']['value']
    data["image"] = sparql.queryAndConvert()['results']['bindings'][0]['image']['value']
    data["rating"] = sparql.queryAndConvert()['results']['bindings'][0]['rating']['value']
    return data

with cc1:
    st.header("User List")
    option = st.selectbox(
        "Select the user",
        ("User 1", "User 2", "User 3", "User 4", "User 5", "User 6", "User 7", "User 8", "User 9", "User 10")
    )
    st.session_state.user_ind = int(option[-1])
    history_uris = get_history_uris("exr:user_" + str(st.session_state.user_ind))
    print(history_uris)
    for uri in history_uris:
        data = get_uri_data(uri)
        title_container = st.container()
        col1, gap, col2 = st.columns([6, 1, 20])
        with title_container:
            with col1:
                st.image(data["image"], width = 80)
            with col2:
                st.markdown(f"**{data['name']}**")
                st.markdown(f"***Price: {data['price']}***")
        st.divider()
    
with cc2:
    st.header("Recommended Products")
    f = open('data/all_products.json')
    data = json.load(f)
    for i in range(10):
        prod_data = data[i]
        stars = int(prod_data["Rating"])
        title_container = st.container()
        col1, gap, col2 = st.columns([6, 1, 20])
        with title_container:
            with col1:
                st.image(prod_data["Image"], width = 80)
            with col2:
                st.markdown(f"**{prod_data['Title']}**")
                st.markdown(f"***Price: {prod_data['Price']}***")
                st.markdown(f"***Rating: {prod_data['Rating']}***")
                
        st.divider()
    
with cc3:
    st.header("Other Users Also Bought")
    items = common_purchase_filter("exr:user_" + str(st.session_state.user_ind))
    for (uri, count) in items:
        if count < 2:
            break
        uri = "exr:" + uri.split('#')[1]
        data = get_uri_data(uri)
        title_container = st.container()
        col1, gap, col2 = st.columns([6, 1, 20])
        with title_container:
            with col1:
                st.image(data["image"], width = 80)
            with col2:
                st.markdown(f"**{data['name']}**")
                st.markdown(f"***Price: {data['price']}***")
                st.markdown(f"***Price: {data['rating']}***")
        st.divider()