import streamlit as st
import pandas as pd
from dataLoader import movieLoader
from surprise import Dataset, Reader, SVD, SVDpp
import queue
import time

RESULTS = queue.Queue() 
SUPPORTED_ALGOS = {"SVD": SVD,"SVD++":SVDpp}

@st.cache_resource(show_spinner="Training baseline models...")
def train_baselines(df):
    reader   = Reader(rating_scale=(0.5, 5))
    trainset = Dataset.load_from_df(
        df[['userId', 'movieId', 'rating']], reader
    ).build_full_trainset()

    models = {}
    for name, Algo in SUPPORTED_ALGOS.items():
        algo = Algo(random_state=42)
        algo.fit(trainset)
        models[name] = algo
    return models

st.set_page_config(layout="wide", page_title="MovieStream", page_icon="🎬")
st.markdown("<h1 style='text-align: center;'>🎬 MovieStream</h1>", unsafe_allow_html=True)

if "mLoader" not in st.session_state:
    placeholder = st.empty()
    mLoader = movieLoader()
    # Show loading message/GIF in the placeholder
    with placeholder.container():
        st.markdown("### Loading movie data...")
        st.markdown("<img src='https://media.giphy.com/media/y1ZBcOGOOtlpC/giphy.gif' width='200'>", unsafe_allow_html=True)
    mLoader.load()
    # Hide the container
    placeholder.empty()
    st.session_state.mLoader = mLoader
else:
    mLoader = st.session_state.mLoader

if "baselines" not in st.session_state:
    ratings_small = pd.DataFrame(mLoader.ratings).sample(1000000)
    start_time = time.time()
    st.session_state.baselines = train_baselines(ratings_small)
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    st.session_state.models_ready = True
    
    st.success(f"✅ Model trained and cached in ⏱️{duration}s")
else:
    if st.session_state.baselines:
        st.success("✅ Cached models ready: " + ", ".join(st.session_state.baselines.keys()))
    else:
        st.warning("⚠️ No models found in cache.")



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
filtered_df = mLoader.movies[mLoader.movies["title"].str.contains(search_value, case=False)] if search_value else mLoader.movies.sample(10)

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



st.html("<h2>Currently hot</h2>")
currentlyHot = mLoader.movies.copy()
currentlyHot.sort_values(by="time_adjusted_rating", ascending=False, inplace=True)
html = '<div class="movie-container">'
for movie in currentlyHot.head(10).itertuples():
    html += showMovie(movie)
html += '</div>'
st.html(html)


for index, row in mLoader.topGenre.head(7).iterrows():
    g = row['index']
    st.html(f"<h2>{g .split('_')[1]}</h2>")
    html = '<div class="movie-container">'
    bestG = mLoader.movies[mLoader.movies[g] == 1].copy()
    bestG["total"] = bestG["avgRating"] * bestG["count"]
    for movie in bestG.sort_values(by="total", ascending=False).head(10).itertuples():
        html += showMovie(movie)
    html += '</div>'
    st.html(html)
    


