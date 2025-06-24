import streamlit as st
import pandas as pd
import json
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
from streamlit_star_rating import st_star_rating
from pathlib import Path

# File to save ratings
USER_RATINGS_PATH = Path("user_ratings.json")

def set_rating(movie_id, rating):
    key = str(movie_id)
    if rating > 0:
        st.session_state.user_ratings[key] = rating
    else:  # rating cleared
        st.session_state.user_ratings.pop(key, None)
    USER_RATINGS_PATH.write_text(json.dumps(st.session_state.user_ratings))

def _render_movie(movie_row: pd.Series):
    """Render a single movie card with star‑rating widget."""
    m_id = int(movie_row.movieId)
    with stylable_container(key=f"movie-{m_id}", css_styles=""):
        st.markdown("---")
        col_img, col_meta = st.columns([1, 2])

        # Poster / placeholder
        with col_img:
            img = (
                movie_row.img
                if pd.notna(movie_row.img) and movie_row.img != ""
                else "https://via.placeholder.com/150x220?text=No+Image"
            )
            st.image(img, width=150)

        # Metadata + rating control
        with col_meta:
            st.markdown(f"### {movie_row.title}")
            st.markdown(f"**Year:** {int(movie_row.year) if not pd.isna(movie_row.year) else '-'}")
            avg_txt = (
                f"⭐ {round(movie_row.avgRating, 1)}"
                if pd.notna(movie_row.avgRating)
                else "unrated"
            )
            st.markdown(f"**Average Rating:** {avg_txt}")
            st.markdown(f"**Genres:** {movie_row.genres if pd.notna(movie_row.genres) else '-'}")

            current = st.session_state.user_ratings.get(str(m_id), 0)
            new_val = st_star_rating(
                label="Your Rating",
                maxValue=5,
                defaultValue=current,
                key=f"star-{m_id}"
            )
            if new_val is not None and new_val != current:
                set_rating(m_id, new_val)
st.set_page_config(page_title="Rate Movies", page_icon="🌟")

if "mLoader" not in st.session_state:
    st.error("Please go to the Home page first to load the data.")
    st.stop()

movies_df: pd.DataFrame = st.session_state.mLoader.movies

if "user_ratings" not in st.session_state:
    if USER_RATINGS_PATH.exists():
        st.session_state.user_ratings = json.loads(USER_RATINGS_PATH.read_text())
    else:
        st.session_state.user_ratings = {}
# A small random sample shown when no search query
if "rated_sample" not in st.session_state:
    st.session_state.rated_sample = (
        movies_df.loc[movies_df["img"].notna() & (movies_df["img"] != "")]
        .sample(5, random_state=42)
        .reset_index(drop=True)
    )

# --------------------------------------------------
# UI: search box
# --------------------------------------------------
search_query = st.text_input("🔍 Search movies to rate (enter ≥3 characters)")

if search_query and len(search_query) >= 3:
    # Case‑insensitive substring match on title
    hits = movies_df[movies_df.title.str.contains(search_query, case=False, na=False)]
    if hits.empty:
        st.info("No movies found.")
    else:
        st.markdown(f"### Results for '**{search_query}**' ({len(hits)} found)")
        for _, row in hits.head(20).iterrows():  # show first 20 results
            _render_movie(row)
else:
    # Default random sample view
    st.markdown("### Random Picks (rate a few to get started)")
    for _, row in st.session_state.rated_sample.iterrows():
        _render_movie(row)

# Button to reset ratings
if st.button("🔄 Reset Ratings"):
    st.session_state.user_ratings = {}
    st.success("User ratings have been reset!")

# Show summary of user ratings
if st.checkbox("✅ Show Your Ratings"):
    rated = [
        {
            "movieId": int(mid),
            "title": movies_df[movies_df.movieId == int(mid)].iloc[0].title,
            "rating": rating
        }
        for mid, rating in st.session_state.user_ratings.items()
    ]
    st.dataframe(pd.DataFrame(rated))

# Button to get recommendations
st.page_link("pages/Web_of_movies.py", label="👉 Go to recommendations", icon="🎬")
