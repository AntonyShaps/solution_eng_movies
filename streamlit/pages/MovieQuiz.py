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
    st.session_state.user_ratings[str(movie_id)] = rating
    USER_RATINGS_PATH.write_text(json.dumps(st.session_state.user_ratings))
st.set_page_config(page_title="Rate Movies", page_icon="🌟")

if "mLoader" not in st.session_state:
    st.error("Please go to the Home page first to load the model.")
else:
    df = st.session_state.mLoader.movies
    ratings = st.session_state.mLoader.ratings
    

    # Initialize session state
    if "rated_sample" not in st.session_state:
        st.session_state.rated_sample = df.loc[df['img'].notna() & (df['img'] != '')].sample(5).reset_index(drop=True)
    if "user_ratings" not in st.session_state:
        if USER_RATINGS_PATH.exists():
            st.session_state.user_ratings = json.loads(USER_RATINGS_PATH.read_text())
        else:
            st.session_state.user_ratings = {}
    
    for idx, movie in st.session_state.rated_sample.iterrows():
        with stylable_container(key=f"movie-container-{idx}",css_styles=""):
            st.markdown("---")
            cols = st.columns([1, 2])
            with cols[0]:
                if pd.isna(movie.img) or movie.img == "":
                    st.image("https://via.placeholder.com/150x220?text=No+Image", width=150)
                else:
                    st.image(movie.img, width=150)

            with cols[1]:
                st.markdown(f"### {movie.title}")
                st.markdown(f"**Year:** {int(movie.year) if not pd.isna(movie.year) else '-'}")
                st.markdown(f"**Average Rating:** {'⭐ ' + str(round(movie.avgRating, 1)) if not pd.isna(movie.avgRating) else 'unrated'}")
                st.markdown(f"**Genres:** {str(movie.genres) if not pd.isna(movie.genres) else '-'}")

                current_rating = st.session_state.user_ratings.get(str(movie.movieId), 0)
                new_rating = st_star_rating(label="Your Rating", maxValue=5, defaultValue=current_rating, key=str(movie.movieId))
                if new_rating is not None:
                    set_rating(movie.movieId, new_rating)

    # Show summary of user ratings
    if st.checkbox("✅ Show Your Ratings"):
        rated = [
            {
                "movieId": int(mid),
                "title": df[df.movieId == int(mid)].iloc[0].title,
                "rating": rating
            }
            for mid, rating in st.session_state.user_ratings.items()
        ]
        st.dataframe(pd.DataFrame(rated))

    # Button to get recommendations
    if st.button("🎯 Get Recommendations"):
        switch_page("web of movies")