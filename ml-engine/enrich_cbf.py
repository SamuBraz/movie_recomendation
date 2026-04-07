"""
Script para enriquecer cbf_df.csv com dados da API do TMDB.
Novos campos: overview, tagline, tmdb_rating, tmdb_votes,
              imdb_rating, imdb_votes, keywords, cast, director

Uso: python3 enrich_cbf.py
"""

import pandas as pd
import requests
import re
import sys
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# --------------------------------------------------------------------------- #
# Configuração
# --------------------------------------------------------------------------- #
TMDB_TOKEN = (
    "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2Y2IzYjI2ZGIxNmVhYTQwODZkNmU2OTQ1ZTZjND"
    "g1ZSIsIm5iZiI6MTc3MjIxODk1MC4zOTEsInN1YiI6IjY5YTFlYTQ2ZjY0YTdkMGQ0YWNjYzg"
    "0OCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.fLJ1Hmp3HDaKvRK92Y1QC"
    "1yV_yAZBW17bB2vwack18Y"
)
BASE_URL = "https://api.themoviedb.org/3/movie"
HEADERS = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LINKS_CSV = BASE_DIR / "ml-latest-small" / "links.csv"
INPUT_CSV = DATA_DIR / "cbf_df.csv"
OUTPUT_CSV = DATA_DIR / "cbf_df.csv"

TOP_CAST = 5
MAX_WORKERS = 20   # requisições paralelas (dentro do limite TMDB de 50/s)

# Lock para o contador de progresso
_lock = threading.Lock()
_done = 0

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def fetch_movie(tmdb_id: int) -> dict:
    """Busca detalhes + keywords + credits em uma única chamada."""
    url = f"{BASE_URL}/{tmdb_id}?append_to_response=keywords,credits&language=en-US"
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                import time; time.sleep(2)
            else:
                return {}
        except Exception:
            import time; time.sleep(1)
    return {}


def extract_keywords(data: dict) -> str:
    kws = data.get("keywords", {}).get("keywords", [])
    return " ".join(k["name"].replace(" ", "") for k in kws)


def extract_cast(data: dict, top: int = TOP_CAST) -> str:
    cast = data.get("credits", {}).get("cast", [])[:top]
    return " ".join(c["name"].replace(" ", "") for c in cast)


def extract_director(data: dict) -> str:
    crew = data.get("credits", {}).get("crew", [])
    directors = [c["name"].replace(" ", "") for c in crew if c.get("job") == "Director"]
    return " ".join(directors)


def extract_year(title: str) -> str:
    m = re.search(r"\((\d{4})\)", title)
    return m.group(1) if m else ""


def build_geral(row: pd.Series) -> str:
    """
    String para TF-IDF — exclui: tmdb_id, imdb_id, tmdb_rating,
    tmdb_votes, imdb_rating, imdb_votes (apenas campos textuais).
    """
    parts = [
        str(row.get("title", "")),
        str(row.get("year", "")),
        str(row.get("genres", "")).replace("|", " "),
        str(row.get("overview", "")),
        str(row.get("tagline", "")),
        str(row.get("keywords", "")),
        str(row.get("cast", "")),
        str(row.get("director", "")),
    ]
    clean = [p for p in parts if p and p not in ("nan", "None", "")]
    return " ".join(clean)


def process_row(args):
    """Processa uma linha do DataFrame e retorna o dicionário enriquecido."""
    global _done
    _, row = args

    tmdb_id = row.get("tmdbId")
    imdb_raw = row.get("imdbId")

    imdb_id = f"tt{int(imdb_raw):07d}" if pd.notna(imdb_raw) else ""
    year = extract_year(str(row["titulo_movie_lens"]))

    overview = tagline = tmdb_rating = tmdb_votes = ""
    keywords = cast = director = ""
    imdb_rating = imdb_votes = ""

    if pd.notna(tmdb_id) and tmdb_id > 0:
        data = fetch_movie(int(tmdb_id))
        if data:
            overview    = data.get("overview", "")   or ""
            tagline     = data.get("tagline", "")    or ""
            tmdb_rating = data.get("vote_average", "")
            tmdb_votes  = data.get("vote_count", "")
            keywords    = extract_keywords(data)
            cast        = extract_cast(data)
            director    = extract_director(data)

    new_row = {
        "movie_id":    int(row["movieId"]),
        "title":       row["titulo_movie_lens"],
        "genres":      row["genres"],
        "year":        year,
        "tmdb_id":     int(tmdb_id) if pd.notna(tmdb_id) else "",
        "imdb_id":     imdb_id,
        "overview":    overview,
        "tagline":     tagline,
        "tmdb_rating": tmdb_rating,
        "tmdb_votes":  tmdb_votes,
        "imdb_rating": imdb_rating,
        "imdb_votes":  imdb_votes,
        "keywords":    keywords,
        "cast":        cast,
        "director":    director,
    }

    with _lock:
        _done += 1
        if _done % 200 == 0:
            print(f"  [{_done}] processados...", flush=True)

    return new_row


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    print("Lendo arquivos de entrada…")
    df_current = pd.read_csv(INPUT_CSV)
    df_links   = pd.read_csv(LINKS_CSV)

    df_current["movieId"] = df_current["movieId"].astype(int)
    df_links["movieId"]   = df_links["movieId"].astype(int)

    df = df_current.merge(df_links, on="movieId", how="left")
    total = len(df)
    print(f"Total de filmes: {total} | Workers paralelos: {MAX_WORKERS}")

    rows = [None] * total
    row_list = list(df.iterrows())

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_row, item): i for i, item in enumerate(row_list)}
        for future in as_completed(futures):
            idx = futures[future]
            rows[idx] = future.result()

    print(f"\nConstruindo DataFrame final ({total} filmes)…")
    df_new = pd.DataFrame(rows)
    df_new["geral"] = df_new.apply(build_geral, axis=1)

    print(f"Salvando em {OUTPUT_CSV}…")
    df_new.to_csv(OUTPUT_CSV, index=False)
    print("Concluído!")
    print(df_new[["movie_id", "title", "tmdb_rating", "keywords", "director"]].head(3).to_string())


if __name__ == "__main__":
    main()
