import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

# 1. Carregar o links.csv
links = pd.read_csv('ml-engine/ml-latest-small/links.csv')
movies = pd.read_csv('ml-engine/ml-latest-small/movies.csv')

def get_poster_path(tmdb_id):
    if pd.isna(tmdb_id):
        return None
    api_key = "6cb3b26db16eaa4086d6e6945e6c485e"
    url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}?api_key={api_key}"
    try:
        response = requests.get(url).json()
        poster_path = response.get('poster_path')
        if poster_path:
            print(f"https://image.tmdb.org/t/p/w500{poster_path}")
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except:
        print("erro!")
        return None


def separa_ano_v2(titulo):
    year = titulo[-5:-1]
    name = titulo[:-6].strip()
    return pd.Series([name, year], index=['title', 'year'])



if __name__ == '__main__':
    novas_colunas = movies['titulo_movie_lens'].apply(separa_ano_v2)
    movies = pd.concat([movies, novas_colunas], axis=1)
    movies = movies.drop('titulo_movie_lens', axis=1)
    movies = movies[['movieId', 'title', 'year', 'genres']]
    movies = movies.merge(links[['movieId', 'tmdbId']], on='movieId', how='left')
    movies['tmdbId'] = movies['tmdbId'].astype('Int64')

    ids = movies['tmdbId'].tolist()

    with ThreadPoolExecutor(max_workers=20) as executor:
        posters = list(executor.map(get_poster_path, ids))

    movies['poster_url'] = posters


    movies = movies.drop('tmdbId', axis=1)

    movies.to_csv('teste2.csv', index=False)









