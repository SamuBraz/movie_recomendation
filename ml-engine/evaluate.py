"""
Script de avaliação comparativa: cbf_df.csv vs cbf1.csv
Roda validar_modelo_completo para k in [10, 20, 30, 40, 50, 100]
e verifica_genericidade para cada CSV.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
SPLIT_DIR = Path(__file__).parent / "data_spliting"
USERS_DIR = Path(__file__).parent / "filmes_recomendados_users"

K_VALUES = [10, 20, 30, 40, 50, 100]

# --------------------------------------------------------------------------- #

def build_cosine_matrix(df):
    lista = df["geral"].tolist()
    cvec = CountVectorizer(stop_words="english", ngram_range=(1, 2))
    sf = cvec.fit_transform(lista)
    tfidf = TfidfTransformer().fit_transform(sf)
    print(f"  Matriz TF-IDF: {tfidf.shape}")
    return cosine_similarity(tfidf, tfidf)


def build_pop_score():
    df_rc = pd.read_csv(DATA_DIR / "movies_ratings_count.csv")
    log_r = np.log1p(df_rc["count_ratings"].to_numpy())
    return (log_r - log_r.min()) / (log_r.max() - log_r.min())


def recomendar_filmes_perfil(user_id, movies_df, cosine_sim_matrix, pop_score, n_recomendacoes=50, df_traing_path='data_spliting/traing.csv'):

    # 1. Carregar o histórico de treino do usuário
    df_traing = pd.read_csv(df_traing_path)

    # 2. Identificar os IDs dos filmes que o usuário já assistiu
    df_user = df_traing.loc[df_traing['userId'] == user_id]
    list_id_movies = df_user['movieId'].to_list()

    # 3. Mapear esses IDs para os índices numéricos
    indices_usuario = movies_df[movies_df['movie_id'].isin(list_id_movies)].index.tolist()

    if not indices_usuario:
        return pd.DataFrame()

    # 4. Cálculo da Recomendação por Perfil (Similaridade Média)
    sim_scores_total = np.mean(cosine_sim_matrix[indices_usuario], axis=0)

    # Normalização para aplicar o popularity bias
    max_sim = sim_scores_total.max()
    if max_sim > 0:
        sim_scores_total = sim_scores_total / max_sim

    peso_conteudo = 0.8
    peso_pop = 0.2
    score_hibrido = (sim_scores_total * peso_conteudo) + (pop_score * peso_pop)

    sim_scores = list(enumerate(score_hibrido))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores_filtrados = [s for s in sim_scores if s[0] not in indices_usuario]

    top_sim_scores = sim_scores_filtrados[:n_recomendacoes]
    filme_indices = [i[0] for i in top_sim_scores]

    recomendacoes = movies_df.iloc[filme_indices][['movie_id', 'title']].copy()
    recomendacoes['score_recomendacao'] = [i[1] for i in top_sim_scores]

    return recomendacoes


def validar_modelo_completo(movies_df, cosine_sim, pop_score, df_training, df_testing, k, csv_label):
    usuarios = df_testing["userId"].unique()
    total_precision = total_recall = contagem = 0
    id_col = "movie_id" if "movie_id" in movies_df.columns else "movieId"

    user_recs = {}
    for user_id in usuarios:
        filmes_reais = set(df_testing[df_testing["userId"] == user_id]["movieId"])
        rec_df = recomendar_filmes_perfil(user_id, movies_df, cosine_sim, pop_score, n_recomendacoes=k, df_traing_path=str(SPLIT_DIR / "traing.csv"))
        if rec_df.empty:
            continue
        recomendados = set(rec_df["movie_id"])
        hits = len(recomendados & filmes_reais)
        total_precision += hits / k
        total_recall += hits / len(filmes_reais)
        contagem += 1
        user_recs[user_id] = list(rec_df["movie_id"])

    return {
        "csv": csv_label,
        "k": k,
        "precision": total_precision / contagem if contagem else 0,
        "recall": total_recall / contagem if contagem else 0,
        "usuarios": contagem,
        "user_recs": user_recs,
    }


def verificar_genericidade(user_recs, movies_df, top_n=10):
    id_col = "movie_id" if "movie_id" in movies_df.columns else "movieId"
    title_col = "title" if "title" in movies_df.columns else "titulo_movie_lens"
    todas = []
    for recs in user_recs.values():
        todas.extend(recs)
    contagem = Counter(todas)
    result = []
    for mid, freq in contagem.most_common(top_n):
        titulo = movies_df[movies_df[id_col] == mid][title_col].values
        titulo = titulo[0] if len(titulo) > 0 else "N/A"
        result.append({"movie_id": mid, "title": titulo, "freq": freq})
    return result


# --------------------------------------------------------------------------- #

def avaliar_csv(csv_path, label):
    print(f"\n{'='*60}")
    print(f"Avaliando: {label} ({csv_path.name})")
    print(f"{'='*60}")

    movies_df = pd.read_csv(csv_path)
    print(f"  Shape: {movies_df.shape}")

    print("  Construindo matriz TF-IDF...")
    cosine_sim = build_cosine_matrix(movies_df)
    pop_score  = build_pop_score()

    df_training = pd.read_csv(SPLIT_DIR / "traing.csv")
    df_testing  = pd.read_csv(SPLIT_DIR / "testing.csv")

    resultados = []
    for k in K_VALUES:
        print(f"  Rodando k={k}...", end=" ", flush=True)
        res = validar_modelo_completo(
            movies_df, cosine_sim, pop_score, df_training, df_testing, k, label
        )
        print(f"Precision={res['precision']:.4f}  Recall={res['recall']:.4f}")
        resultados.append(res)

    # Generalização com k=100 (maior k testado)
    print("  Calculando generalização (k=100)...")
    res_k100 = next(r for r in resultados if r["k"] == 100)
    generic = verificar_genericidade(res_k100["user_recs"], movies_df)

    return resultados, generic


# --------------------------------------------------------------------------- #

def build_readme(results_cbf, generic_cbf, results_cbf1, generic_cbf1):
    lines = []
    lines.append("# Avaliação do Motor CBF — Comparativo `cbf_df.csv` vs `cbf1.csv`\n")
    lines.append(
        "Métricas calculadas com **Mean Precision@K** e **Mean Recall@K** "
        "sobre o conjunto de teste, variando K em `[10, 20, 30, 40, 50, 100]`.\n"
    )
    lines.append(
        "O motor usa TF-IDF + Similaridade de Cosseno com popularity bias (80/20).\n"
    )

    def tabela(results, label):
        out = [f"## {label}\n"]
        out.append("| K | Mean Precision@K | Mean Recall@K | Usuários Avaliados |")
        out.append("|---|---|---|---|")
        for r in results:
            out.append(
                f"| {r['k']} | {r['precision']:.4f} | {r['recall']:.4f} | {r['usuarios']} |"
            )
        return "\n".join(out) + "\n"

    def gen_table(generic, label):
        out = [f"### Generalização — {label} (Top 10 filmes mais recomendados, k=100)\n"]
        out.append("| Posição | Movie ID | Título | Nº de Usuários |")
        out.append("|---|---|---|---|")
        for i, g in enumerate(generic, 1):
            out.append(f"| {i} | {g['movie_id']} | {g['title']} | {g['freq']} |")
        return "\n".join(out) + "\n"

    lines.append(tabela(results_cbf, "cbf_df.csv — Sem tags de usuários"))
    lines.append(tabela(results_cbf1, "cbf1.csv — Com tags de usuários"))

    # Comparativo side-by-side
    lines.append("## Comparativo direto\n")
    lines.append("| K | Precision cbf | Precision cbf1 | Recall cbf | Recall cbf1 |")
    lines.append("|---|---|---|---|---|")
    for r0, r1 in zip(results_cbf, results_cbf1):
        delta_p = r1["precision"] - r0["precision"]
        delta_r = r1["recall"] - r0["recall"]
        sign_p = "+" if delta_p >= 0 else ""
        sign_r = "+" if delta_r >= 0 else ""
        lines.append(
            f"| {r0['k']} "
            f"| {r0['precision']:.4f} "
            f"| {r1['precision']:.4f} ({sign_p}{delta_p:.4f}) "
            f"| {r0['recall']:.4f} "
            f"| {r1['recall']:.4f} ({sign_r}{delta_r:.4f}) |"
        )
    lines.append("")

    lines.append(gen_table(generic_cbf,  "cbf_df.csv"))
    lines.append(gen_table(generic_cbf1, "cbf1.csv"))

    # Notas sobre o dataset
    lines.append("## Notas sobre os datasets\n")
    lines.append(
        "- **cbf_df.csv**: enriquecido com dados da API TMDB — overview, tagline, "
        "keywords, cast (top 5), director. A coluna `geral` usa apenas campos textuais "
        "(exclui IDs e ratings numéricos).\n"
    )
    lines.append(
        "- **cbf1.csv**: idem ao anterior, acrescido da coluna `tags` — "
        "agregação das tags inseridas pelos usuários do MovieLens (`tags.csv`), "
        "unidas com `|` por filme. Apenas **1.571 de 9.708** filmes possuem tags.\n"
    )

    return "\n".join(lines)


# --------------------------------------------------------------------------- #

def main():
    results_cbf,  generic_cbf  = avaliar_csv(DATA_DIR / "cbf_df.csv", "cbf_df.csv")
    results_cbf1, generic_cbf1 = avaliar_csv(DATA_DIR / "cbf1.csv",   "cbf1.csv")

    readme_path = Path(__file__).parent.parent / "README.md"
    content = build_readme(results_cbf, generic_cbf, results_cbf1, generic_cbf1)
    readme_path.write_text(content, encoding="utf-8")
    print(f"\nREADME.md gerado em: {readme_path}")


if __name__ == "__main__":
    main()
