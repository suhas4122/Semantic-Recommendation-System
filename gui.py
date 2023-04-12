import streamlit as st

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
        ("User 1", "User 2", "User 3", "User 4", "User 5", "User 6", "User 7", "User 8", "User 9", "User 10")
    )
    
    st.text("A Laptop")
    st.image("https://m.media-amazon.com/images/I/41dgHDQs4RL._SX300_SY300_QL70_ML2_.jpg", width=200)
    st.divider()
    
    st.text("A Phone")
    st.image("https://m.media-amazon.com/images/I/31gu9jL+eDL._SY300_SX300_.jpg", width=200)
    st.divider()
    
    st.text("An Jewellery")
    st.image("https://m.media-amazon.com/images/W/IMAGERENDERING_521856-T1/images/I/51fU-iWByBL.jpg", width=200)
    
with cc2:
    st.header("Recommended Products")
    
with cc3:
    st.header("Other Users Also Bought")
    