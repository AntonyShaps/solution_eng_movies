import streamlit as st
import pandas as pd
import json
from pathlib import Path
from surprise import Dataset, Reader, SVD
import dataLoader

st.set_page_config(page_title="Graph", page_icon="🕸️")

st.title("Recommendations")

if "mLoader" not in st.session_state:
    st.warning("Please go to homepage to load the data")
else:
    USER_RATINGS_PATH = Path("user_ratings.json")
    if not USER_RATINGS_PATH.exists():
        st.warning("No user ratings found. Please rate some movies first.")
        st.stop()
    movies_df =  pd.DataFrame(st.session_state.mLoader.movies)
    ratings_df = pd.DataFrame(st.session_state.mLoader.ratings)
    user_ratings = json.loads(USER_RATINGS_PATH.read_text())
    ratings_small = ratings_df.sample(10000)
    model_options = ["SVD"]
    selected_model = st.selectbox("Select Recommendation Model", model_options)
    
    reader = Reader(rating_scale=(0.5, 5))
    data = Dataset.load_from_df(ratings_small[['userId', 'movieId', 'rating']], reader)
    trainset = data.build_full_trainset()

    if selected_model == "SVD":
        model = SVD()
    else:
        st.warning("No/Invalid Model Selected.")
        st.stop()
    model.fit(trainset)

    # Predict ratings for unseen movies
    all_movie_ids = set(movies_df.movieId)
    rated_movie_ids = set(map(int, user_ratings.keys()))
    unseen_movie_ids = all_movie_ids - rated_movie_ids

    fake_user_id = 9999  # Dummy ID for prediction
    predictions = []
    for movieid in unseen_movie_ids:
        pred = model.predict(fake_user_id, movieid, verbose=False)
        predictions.append((movieid, pred.est))

    top_n = sorted(predictions, key=lambda x: x[1], reverse=True)[:10]
    top_movies = pd.DataFrame(top_n, columns=["movieId", "predicted_rating"])
    top_movies = pd.merge(top_movies, movies_df, on="movieId")
    
    for _, row in top_movies.iterrows():
        with st.container():
            cols = st.columns([1, 4])
            with cols[0]:
                if pd.isna(row["img"]) or row["img"] == "":
                    img = st.session_state.mLoader.loadPicture(row["movieId"], row["imdbId"], row["tmdbId"])
                else:
                    img = row["img"]
                st.image(img, width=120)
            with cols[1]:
                st.subheader(row["title"])
                st.markdown(f"**Predicted Rating:** ⭐ {round(row['predicted_rating'], 2)}")
                st.markdown(f"**Year:** {int(row['year']) if not pd.isna(row['year']) else '-'}")



