import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path
from surprise import Dataset, Reader, SVD, SVDpp
import dataLoader
import NeuMF_Loader
import time
from sklearn.metrics.pairwise import cosine_similarity
import copy
from datetime import datetime


st.set_page_config(page_title="Recommendations", page_icon="🕸️")

# Fine tune function: retrain a bit on combined ratings
def quick_finetune(baseline_algo, combined_ratings_df, epochs=5, lr=0.001):
    reader = Reader(rating_scale=(0.5, 5))
    trainset = Dataset.load_from_df(combined_ratings_df[['userId', 'movieId', 'rating']], reader).build_full_trainset()

    tuned = copy.deepcopy(baseline_algo)
    tuned.n_epochs = epochs
    tuned.lr_all = lr
    tuned.fit(trainset)
    return tuned, trainset

if "mLoader" not in st.session_state:
    st.warning("Please go to homepage to load the data")


if not st.session_state.get("baselines"):
    st.error("Baseline models not ready. Go to Home and wait for training to finish.")
    st.stop()

if not st.session_state.get("NeuMF4_loaded"):
    st.error("NeuMF4 model not loaded. Go to Home and wait for it to load.")
    st.stop()

USER_RATINGS_PATH = Path("user_ratings.json")
if not USER_RATINGS_PATH.exists():
    st.warning("No user ratings found. Please rate some movies first.")
    st.stop()

movies_df =  pd.DataFrame(st.session_state.mLoader.movies)
ratings_df = pd.DataFrame(st.session_state.mLoader.ratings)

model_options = list(('NeuMF4', *st.session_state.baselines.keys()))

selected_model = st.selectbox("Select Recommendation Model", model_options)

if selected_model == "NeuMF4":
    start_time = time.time()
    NeuMF4_model = st.session_state.NeuMF4
    datasetNeuMF = st.session_state.datasetNeuMF
    try:
        predictions_df = NeuMF_Loader.predict_for_cold_start_user_from_json(
            NeuMF4_model, datasetNeuMF, './user_ratings.json'
        )
        with open('./user_ratings.json', 'r') as f:
            user_raw_ratings = json.load(f)
        predictions_df["movieId"] = predictions_df["movieId"].astype(int)
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        st.stop()

    top_movies = (predictions_df
                .sort_values("predicted_rating", ascending=False)
                .merge(movies_df, on="movieId"))

    end_time = time.time()
    duration = round(end_time - start_time, 2)
    st.header(f"Top 50 picks via NeuMF4 model ⏱️{duration}s")
    st.markdown(f"**Note:** last prediction was made at {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')} based on {len(user_raw_ratings)} movies rated by you.")

    for _, row in top_movies.iterrows():
        with st.container():
            c1, c2 = st.columns([1, 4])
            with c1:
                img = row["img"] if pd.notna(row["img"]) and row["img"] else \
                    st.session_state.mLoader.loadPicture(row.movieId, row.imdbId, row.tmdbId)
                st.image(img, width=120)
            with c2:
                st.subheader(row.title)
                st.markdown(f"**Their rating:** ⭐ {row.predicted_rating:.2f}")
                st.markdown(f"**Year:** {int(row.year) if not pd.isna(row.year) else '-'}")



if selected_model in st.session_state.baselines.keys():
    user_ratings = json.loads(USER_RATINGS_PATH.read_text())
    user_id = 9999999  # fake ID for current user
    user_rows = [{
        "userId": user_id,
        "movieId": int(mid),
        "rating": float(rating)
    } for mid, rating in user_ratings.items()]
    combined_ratings_df = pd.concat([ratings_df, pd.DataFrame(user_rows)], ignore_index=True)

    start_time = time.time()
    baseline = st.session_state.baselines[selected_model]
    model, trainset = quick_finetune(baseline, combined_ratings_df)

    try:
        inner_uid_cur = trainset.to_inner_uid(user_id)
    except ValueError:
        st.error("Current user not found in trainset")
        st.stop()

        
    # User embedding vector
    cur_vec = model.pu[inner_uid_cur].reshape(1, -1)

    # Compute cosine similarity between current user and all other users in the model
    sims = cosine_similarity(cur_vec, model.pu).flatten()
    sims[inner_uid_cur] = -1  # exclude self

    inner_uid_similar = sims.argmax()
    similar_uid = trainset.to_raw_uid(inner_uid_similar)

    # Fetch similar user's ratings
    similar_user_ratings = ratings_df[ratings_df.userId == similar_uid]
    similar_user_df = similar_user_ratings.merge(movies_df, on="movieId")

    top_movies = (similar_user_ratings
                .sort_values("rating", ascending=False)
                .head(10)
                .merge(movies_df, on="movieId"))

    end_time = time.time()
    duration = round(end_time - start_time, 2)

    st.header(f"Top picks via your most similar user (id {similar_uid})  ⏱️{duration}s")
    st.write(f"Similarity with user {similar_uid}: {sims[inner_uid_similar]:.2f}")

    for _, row in top_movies.iterrows():
        with st.container():
            c1, c2 = st.columns([1, 4])
            with c1:
                img = row["img"] if pd.notna(row["img"]) and row["img"] else \
                    st.session_state.mLoader.loadPicture(row.movieId, row.imdbId, row.tmdbId)
                st.image(img, width=120)
            with c2:
                st.subheader(row.title)
                st.markdown(f"**Their rating:** ⭐ {row.rating}")
                st.markdown(f"**Year:** {int(row.year) if not pd.isna(row.year) else '-'}")
    with st.expander("🔍 Explore similar user's full profile"):
        st.markdown("#### Quick stats")
        total_rated = len(similar_user_df)
        avg_rating  = similar_user_df.rating.mean()
        st.write(f"Movies rated: {total_rated:,}")
        st.write(f"Average rating: {avg_rating:.2f}")

        # Rating distribution
        hist = np.histogram(similar_user_df.rating, bins=np.arange(0.5, 5.5, 0.5))
        st.bar_chart(pd.DataFrame({"rating": hist[0]}, index=[f"{b:.1f}" for b in hist[1][:-1]]))

        # Search box
        search = st.text_input("Filter by title (min 2 chars)")
        filtered_df = (
            similar_user_df[similar_user_df.title.str.contains(search, case=False, na=False)] if search and len(search) >= 2 else similar_user_df
        )

        # Sort selector
        sort_by = st.selectbox("Sort by", ["rating desc", "rating asc", "year desc", "year asc", "title"])
        ascending = "asc" in sort_by
        key = sort_by.split()[0]
        filtered_df = filtered_df.sort_values(key if key != "rating" else "rating", ascending=ascending)

# Show results (first 30)
st.markdown(f"### Showing {len(filtered_df)} movies")
for _, row in filtered_df.head(30).iterrows():
    with st.container():
        c1, c2 = st.columns([1, 4])
        with c1:
            img = row["img"] if pd.notna(row["img"]) and row["img"] else "https://via.placeholder.com/100x150?text=No+Image"
            st.image(img, width=100)
        with c2:
            st.markdown(f"**{row.title}** ({int(row.year) if not pd.isna(row.year) else '-'})")
            st.markdown(f"Rating: ⭐ {row.rating}")
            st.markdown(f"Genres: {row.genres if pd.notna(row.genres) else '-'}")