import streamlit as st
import pandas as pd

# Sample movie data
movies = [
    {"title": "Inception", "rating": 8.8, "genre": "Sci-Fi", "image": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_FMjpg_UX1000_.jpg"},
    {"title": "Interstellar", "rating": 8.6, "genre": "Sci-Fi", "image": "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg"},
    {"title": "The Dark Knight", "rating": 9.0, "genre": "Action", "image": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_FMjpg_UX1000_.jpg"},
    {"title": "Tenet", "rating": 7.5, "genre": "Action", "image": "https://m.media-amazon.com/images/M/MV5BMTU0ZjZlYTUtYzIwMC00ZmQzLWEwZTAtZWFhMWIwYjMxY2I3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"},
    {"title": "Coco", "rating": 8.4, "genre": "Animation", "image": "https://lumiere-a.akamaihd.net/v1/images/p_coco_19736_fd5fa537.jpeg"},
    {"title": "Up", "rating": 8.2, "genre": "Animation", "image": "https://upload.wikimedia.org/wikipedia/en/0/05/Up_%282009_film%29.jpg"},
]

df = pd.DataFrame(movies)

st.set_page_config(layout="wide", page_title="MovieStream", page_icon="🎬")
st.markdown("<h1 style='text-align: center;'>🎬 MovieStream</h1>", unsafe_allow_html=True)

# --- Search Bar ---
def update_search():
    st.session_state.search_value = st.session_state.search_input

st.text_input(
    "🔍 Search for a movie",
    placeholder="e.g. Inception, Up",
    key="search_input",
    on_change=update_search
)

search_value = st.session_state.get("search_value", "")
filtered_df = df[df["title"].str.contains(search_value, case=False)] if search_value else df

# --- Featured Movies ---
st.markdown("### 🔥 Featured")
with st.container():
    cols = st.columns(len(filtered_df.head(6)))
    for col, row in zip(cols, filtered_df.head(6).itertuples()):
        with col:
            st.markdown(f"<img src='{row.image}' style='width:150px; border-radius:10px;'/>", unsafe_allow_html=True)
            st.markdown(f"**{row.title}**")
            st.markdown(f"⭐ {row.rating}")

st.markdown("---")

# --- Genre Sections ---
genres = df["genre"].unique()
for genre in genres:
    st.markdown(f"## 🎞️ {genre}")
    genre_movies = df[df["genre"] == genre]

    scroll_container = st.container()
    with scroll_container:
        cols = st.columns(len(genre_movies))
        for col, row in zip(cols, genre_movies.itertuples()):
            with col:
                st.markdown(f"<img src='{row.image}' style='width:150px; border-radius:10px;'/>", unsafe_allow_html=True)
                st.markdown(f"**{row.title}**")
                st.markdown(f"⭐ {row.rating}")
