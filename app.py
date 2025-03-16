import streamlit as st
import pickle
import requests
import os


# Function to fetch the movie poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=bb8706490c17e3e08cd77b68988dd6e5&language=en-US"
    
    try:
        response = requests.get(url, timeout=5)  # Set timeout to avoid infinite waiting
        response.raise_for_status()  # Raise error if request fails
        data = response.json()

        if 'poster_path' in data and data['poster_path']:
            return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Image+Unavailable"

# Function to get movie recommendations
def recommend(movie):
    movie_idx = movies[movies['title'] == movie].index

    if movie_idx.empty:
        st.warning(f"⚠️ Movie '{movie}' not found in dataset.")
        return [], []

    index = movie_idx[0]  # Get index of the selected movie
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movies_name = []
    recommended_movies_poster = []
    
    for i in distances[1:6]:  # Get top 5 recommended movies
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_movies_poster.append(fetch_poster(movie_id))
        recommended_movies_name.append(movies.iloc[i[0]]['title'])
    
    return recommended_movies_name, recommended_movies_poster

# Streamlit App UI
st.header("🎬 Movies Recommendation System Using Machine Learning")

# Load the pickle files safely
try:
    movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("❌ Movie data files not found! Ensure `movie_list.pkl` and `similarity.pkl` exist in the `artifacts` folder.")
    st.stop()

# Get movie list for selection
movie_list = movies['title'].values
selected_movie = st.selectbox(
    '🎥 Type or Select a Movie to get recommendations',
    movie_list
)

if st.button('🔍 Show Recommendations'):
    recommended_movies_name, recommended_movies_poster = recommend(selected_movie)

    if recommended_movies_name:
        cols = st.columns(len(recommended_movies_name))  # Adjust column count dynamically

        for col, movie_name, movie_poster in zip(cols, recommended_movies_name, recommended_movies_poster):
            with col:
                st.text(movie_name)
                st.image(movie_poster)
    else:
        st.error("❌ No recommendations found. Try another movie.")
