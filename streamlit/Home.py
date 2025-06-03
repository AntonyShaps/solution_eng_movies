import streamlit as st
import pandas as pd
from dataLoader import movieLoader

st.set_page_config(layout="wide", page_title="MovieStream", page_icon="🎬")
st.markdown("<h1 style='text-align: center;'>🎬 MovieStream</h1>", unsafe_allow_html=True)

mLoader = movieLoader()
st.session_state.mLoader = mLoader

placeholder = st.empty()

# Show loading message/GIF in the placeholder
with placeholder.container():
    st.markdown("### Loading movie data...")
    st.markdown("<img src='https://media.giphy.com/media/y1ZBcOGOOtlpC/giphy.gif' width='200'>", unsafe_allow_html=True)

# Run your actual loading function
mLoader.load()


# Hide the container
placeholder.empty()


##Uncoment to load more images
#for movie in mLoader.movies.itertuples():
#    if movie.img == "" or pd.isna(movie.img) or pd.isnull(movie.img):
#        mLoader.loadPicture(movie.movieId, movie.imdbId, movie.tmdbId)




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
filtered_df = mLoader.movies[mLoader.movies["title"].str.contains(search_value, case=False)] if search_value else mLoader.movies

filtered_df.sort_values(by="count", ascending=False, inplace=True)

st.markdown("""
<style>
.movie-container {
    display: flex;
    overflow-x: auto;
    padding-bottom: 10px;
    scroll-behavior: smooth;
}
.movie-card {
    flex: 0 0 16.5%;
    margin: 0 10px;
    background-color: #1e1e1e;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.movie-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.5);
}
.movie-img {
    width: 100%;
    height: 240px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    background-size: cover;
    background-position: center;
}
.movie-content {
    padding: 10px;
    color: white;
    text-align: center;
}
.movie-title {
    font-size: 15px;
    font-weight: bold;
    margin-bottom: 5px;
}
.movie-meta {
    font-size: 13px;
    color: #bbbbbb;
}
</style>
""", unsafe_allow_html=True)


def showMovie(movie):
    year = str(int(movie.year)) if not pd.isna(movie.year) else "-"
    rating = f"⭐ {round(movie.avgRating, 1)}" if not pd.isna(movie.avgRating) else "unrated"
    if movie.img == "" or pd.isna(movie.img) or pd.isnull(movie.img):
        img_url = mLoader.loadPicture(movie.movieId, movie.imdbId, movie.tmdbId)
    else:
        img_url = movie.img

    div = f"""
    <div class="movie-card">
        <div class="movie-img" style="background-image: url('{img_url}');"></div>
        <div class="movie-content">
            <div class="movie-title">{movie.title}</div>
            <div class="movie-meta">
                {year} &bull;
                {rating}
            </div>
        </div>
    </div>
    """

    return div

# Build HTML
html = '<div class="movie-container">'
for movie in filtered_df.head(10).itertuples():
    html += showMovie(movie)


html += '</div>'


st.html(html)



st.html("<h2>All time classics 🏆</h2>")

allTime = mLoader.movies.copy()

allTime["total"] = allTime["avgRating"] * allTime["count"]

allTime.sort_values(by="total", ascending=False, inplace=True)
html = '<div class="movie-container">'
for movie in allTime.head(10).itertuples():
    html += showMovie(movie)


html += '</div>'
st.html(html)
st.html("<h2>Currently hot 🌶️🔥</h2>")


