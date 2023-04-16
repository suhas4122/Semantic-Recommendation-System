import streamlit as st
import recommender
import json
import pandas as pd
import webbrowser

st.set_page_config(
    page_title="Semantic Recommender System",
    page_icon="🎈",
    layout="wide"
)

st.title("Semantic Recommender System")
cc1, pad1, cc2, pad2, cc3 = st.columns([10, 2, 10, 2, 10])

with cc1:
    st.header("User List")
    option = st.selectbox(
        "Select the user",
        ("User 1", "User 2", "User 3", "User 4", "User 5", "User 6", "User 7", "User 8")
    )
    st.session_state.user_ind = int(option[-1])
    recommender.user_ind = st.session_state.user_ind
    recommender.user_uri = "exr:user_" + str(st.session_state.user_ind)
    recommender.history_uris = recommender.get_history_uris()
    recommender.hist_categories = recommender.get_hist_categories()
   
    for uri in recommender.history_uris:
        data = recommender.get_uri_data(uri)
        title_container = st.container()
        col1, gap, col2 = st.columns([8, 1, 20])
        with title_container:
            with col1:
                st.image(data["image"], width = 150)
            with col2:
                st.markdown(f"**{data['name']}**")
                st.markdown(f"***Price: ₹{data['price']}***")
        st.divider()
    
with cc2:
    st.header("Recommended Products")
    df_res = pd.read_csv("results/recs_" + str(st.session_state.user_ind) + ".csv")
    uris = df_res["uris"].tolist()
    for i in range(10):
        uri = uris[i]
        # print(uri)
        data = recommender.get_uri_data(uri)
        title_container = st.container()
        col1, gap, col2 = st.columns([8, 1, 20])
        with title_container:
            with col1:
                st.image(data["image"], width = 150)
            with col2:
                st.markdown(f"**{data['name']}**")
                st.markdown(f"***Price: ₹{data['price']}***")
                st.markdown(f"***Rating: {data['rating']}***")
                if st.button("Buy Now", key = data['link']):
                    webbrowser.open_new_tab(data["link"])
        st.divider()
    
with cc3:
    st.header("Other Users Also Bought")
    items = recommender.common_purchase_filter("exr:user_" + str(st.session_state.user_ind))
    ind = 0
    for (uri, count) in items:
        ind += 1
        if count < 2:
            break
        uri = "exr:" + uri.split('#')[1]
        data = recommender.get_uri_data(uri)
        title_container = st.container()
        col1, gap, col2 = st.columns([8, 1, 20])
        with title_container:
            with col1:
                st.image(data["image"], width = 150)
            with col2:
                st.markdown(f"**{data['name']}**")
                st.markdown(f"***Price: ₹{data['price']}***")
                st.markdown(f"***Rating: {data['rating']}***")
                if st.button("Buy Now", key = str(data['link']) + str(ind)):
                    webbrowser.open_new_tab(data["link"])
        st.divider()