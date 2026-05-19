# Sistema de Recomendação de Filmes

Sistema de recomendação híbrido que combina **Filtragem Baseada em Conteúdo (FBC)** e **Filtragem Colaborativa (FC)** para recomendar filmes personalizados. O arquivo principal é [`ml-engine/hybrid.ipynb`](ml-engine/hybrid.ipynb).

---

## Visão Geral

O sistema funde dois paradigmas de recomendação:

- **FBC (CBFEngine)** — analisa atributos textuais dos filmes (gênero, sinopse, elenco, diretor, palavras-chave) via TF-IDF + similaridade cosseno.
- **FC (CFEngine)** — aprende padrões de avaliação de usuários via fatoração matricial (SVD).
- **Híbrido Cascade (HybridEngine)** — usa a FBC para gerar candidatos e a FC para reordenar, superando ambos individualmente.

---

## Dataset

**MovieLens ml-latest-small** (GroupLens Research)

| Atributo | Valor |
|----------|-------|
| Avaliações | 100.836 |
| Usuários | 610 |
| Filmes | 9.742 |
| Escala de notas | 0.5 – 5.0 (meias estrelas) |
| Período | Mar/1996 – Set/2018 |

Os filmes foram enriquecidos com metadados da **API TMDB** (sinopse, tagline, elenco top-5, diretor, palavras-chave) pelo script [`enrich_cbf.py`](ml-engine/enrich_cbf.py).

---

## Estrutura de Diretórios

```
ml-engine/
├── hybrid.ipynb                  ← arquivo principal (motor híbrido)
├── cbf_engine.ipynb              ← exploração isolada da FBC
├── cf_engine.ipynb               ← exploração isolada da FC
├── spliting_hybrid.ipynb         ← geração do split treino/teste 70/30
├── enrich_cbf.py                 ← enriquecimento via API TMDB
│
├── data/
│   ├── cbf_df.csv                ← 9.708 filmes enriquecidos (entrada da FBC)
│   ├── movies_ratings_count.csv  ← contagem de avaliações por filme (popularidade)
│   └── tags_unique.csv           ← tags únicas do dataset
│
├── data_spliting_hybrid/
│   ├── training.csv              ← 70.595 avaliações (70% por usuário)
│   └── testing.csv               ← 30.241 avaliações (30% por usuário)
│
├── ml-latest-small/              ← dataset bruto MovieLens
│   ├── ratings.csv
│   ├── movies.csv
│   ├── tags.csv
│   └── links.csv
│
├── analises/                     ← notebooks exploratórios
│   ├── analise_exploratoria.ipynb
│   ├── analise_recomendacoes.ipynb
│   ├── analises_rating.ipynb
│   └── ratings_analise.ipynb
│
├── pre-processamento/
│   ├── limpeza.ipynb
│   └── preprocessing.ipynb
│
└── graficos/
    ├── comparativo_modelos.png
    └── comparativo_modelos.pdf
```

---

## Pipeline Completo

```
Dataset bruto (ml-latest-small)
        │
        ▼
pre-processamento/limpeza.ipynb
pre-processamento/preprocessing.ipynb
        │
        ▼
enrich_cbf.py  ──[API TMDB]──► data/cbf_df.csv
                                (title, genres, overview, tagline,
                                 keywords, cast, director → campo "geral")
        │
        ▼
spliting_hybrid.ipynb
        │  split 70/30 por usuário (seed=42)
        ├──► data_spliting_hybrid/training.csv
        └──► data_spliting_hybrid/testing.csv
        │
        ▼
hybrid.ipynb
  ├── CBFEngine   (TF-IDF + cosseno + RRF)
  ├── CFEngine    (SVD via Surprise)
  └── HybridEngine (cascade CBF → CF)
```

---

## Componentes Principais (`hybrid.ipynb`)

### CBFEngine

Recomenda filmes com base na similaridade textual entre filmes.

**Construção do índice:**
1. Carrega `data/cbf_df.csv` — campo `geral` concatena título, gêneros, sinopse, tagline, palavras-chave, elenco e diretor.
2. `CountVectorizer` com bigramas (`ngram_range=(1,2)`), `stop_words='english'`, `max_df=0.85`.
3. `TfidfTransformer` para ponderar termos raros vs. frequentes.
4. Matriz de similaridade cosseno `(9.708 × 9.708)`.
5. Score de popularidade: `log1p(contagem_avaliações)` normalizado min-max.

**Geração de recomendações (`recomendar_filmes_perfil`):**
1. Filtra o histórico do usuário no treino com `rating >= threshold` (padrão 4.0).
2. Aplica **Reciprocal Rank Fusion (RRF)** com `k=60` sobre todos os filmes-semente do perfil.
3. Normaliza por rank (percentil) os scores de conteúdo e popularidade.
4. Score final = `0.9 × sim_conteúdo + 0.1 × popularidade`.

---

### CFEngine

Recomenda filmes prevendo notas com fatoração matricial.

**Modelo:** SVD (biblioteca Surprise)

| Hiperparâmetro | Valor |
|----------------|-------|
| `n_factors` | 100 |
| `n_epochs` | 20 |
| `lr_all` | 0.005 |
| `random_state` | 42 |

O modelo aprende vetores latentes para **610 usuários** e **8.536 filmes**, além de vieses por usuário e por filme.

**Resultados isolados (catálogo completo):**

| Métrica | Valor |
|---------|-------|
| RMSE | 0.8836 |
| MAE | 0.6786 |
| Mean Precision@10 | 0.1223 |
| Mean Recall@10 | 0.0380 |

---

### HybridEngine — Cascade CBF → CF

Estratégia: a FBC filtra candidatos relevantes; a FC reordena dentro desse subconjunto.

**`recomendar(user_id, k_cbf=200, k=10, alpha=0.6)`**

1. **Geração de candidatos:** CBFEngine retorna os `k_cbf=200` filmes mais similares ao perfil do usuário.
2. **Normalização global CF:** para todos os filmes não assistidos (~9k), obtém predições SVD e normaliza por rank (`rank / N_total`).
3. **Normalização local CBF:** normaliza os scores RRF dos 200 candidatos por rank (`rank / k_cbf`).
4. **Fusão (apenas nos candidatos CBF):**

```
score_hibrido = alpha × cbf_norm + (1 - alpha) × cf_norm
```

5. Retorna os `k=10` filmes com maior `score_hibrido`.

> **Parâmetros ótimos encontrados:** `k_cbf=200`, `alpha=0.2`  
> Com `alpha=0.2`, a FC tem peso 80% na fusão, usando a FBC apenas para limitar o espaço de busca.

---

## Resultados

### Cenário 1 — Catálogo Completo (~9k filmes)

Avalia como se o sistema precisasse escolher entre todo o catálogo. Representa o caso real de uso.

| Modelo | Precision@10 | Recall@10 |
|--------|-------------|-----------|
| FBC pura (RRF) | 0.2045 | 0.0755 |
| FC pura (SVD) | 0.1223 | 0.0380 |
| **Híbrido Cascade** | **0.2358** | **0.0827** |

**Ganho do híbrido vs. melhor modelo puro (FBC):** +15.3% Precision · +9.5% Recall

---

### Cenário 2 — Conjunto de Candidatos (filmes do teste por usuário)

Avalia dentro de um pool restrito (média de 77 candidatos por usuário). Representa o teto do modelo — quanto o sistema consegue recuperar quando já sabe quais filmes o usuário vai avaliar.

| Modelo | Precision@10 | Recall@10 |
|--------|-------------|-----------|
| FBC Restrita (RRF) | 0.6935 | 0.3160 |
| FC Restrita (SVD) | 0.7634 | 0.3448 |
| **Híbrido Restrito** | **0.7856** | **0.3518** |

O híbrido supera ambos os modelos isolados em todos os cenários e métricas.

---

## Split Treino/Teste

Gerado em [`spliting_hybrid.ipynb`](ml-engine/spliting_hybrid.ipynb).

- **Estratégia:** split aleatório 70/30 **por usuário** (cada usuário tem exatamente ~30% das suas avaliações no teste).
- **Seed:** `random_state=42`
- **Resultado:** todos os 610 usuários presentes em treino e teste.

| Arquivo | Linhas |
|---------|--------|
| `training.csv` | 70.595 |
| `testing.csv` | 30.241 |

---

## Enriquecimento com TMDB (`enrich_cbf.py`)

Script paralelo (20 workers) que enriquece `data/cbf_df.csv` via API TMDB.

**Campos adicionados por filme:**
- `overview` — sinopse
- `tagline` — slogan
- `tmdb_rating` / `tmdb_votes` — nota e votos no TMDB
- `keywords` — palavras-chave (concatenadas sem espaço)
- `cast` — top-5 atores (nomes sem espaço)
- `director` — diretor(es)

O campo `geral` é reconstruído concatenando todos os campos textuais e alimenta o TF-IDF da FBC.

**Execução:**
```bash
source .venv/bin/activate
python ml-engine/enrich_cbf.py
```

---

## Como Executar

### Pré-requisitos

```bash
# Ativar o ambiente virtual
source .venv/bin/activate
```

### Executar o motor híbrido

Abrir e executar [`ml-engine/hybrid.ipynb`](ml-engine/hybrid.ipynb) do início ao fim. O notebook:

1. Instancia `CBFEngine` (carrega FBC).
2. Instancia `CFEngine` (treina SVD — ~20 épocas).
3. Instancia `HybridEngine`.
4. Gera uma recomendação de exemplo: `hybrid.recomendar(25)`.
5. Valida os três modelos e exibe o comparativo final.

### Reproduzir o split

```bash
# Executar spliting_hybrid.ipynb para regenerar training.csv e testing.csv
```

---

## Dependências Principais

| Biblioteca | Uso |
|-----------|-----|
| `pandas` | manipulação de dados |
| `scikit-learn` | TF-IDF, similaridade cosseno, rankdata |
| `scipy` | rankdata |
| `numpy` | operações vetoriais |
| `surprise` | SVD (Filtragem Colaborativa) |
| `matplotlib` | geração de gráficos |
| `requests` | API TMDB (enrich_cbf.py) |

---

## Métricas Utilizadas

**Precision@K** — dos K filmes recomendados, quantos o usuário consideraria relevantes.

```
Precision@K = hits / K
```

**Recall@K** — dos filmes relevantes do usuário no teste, quantos aparecem entre os K recomendados.

```
Recall@K = hits / |filmes_relevantes_no_teste|
```

Um filme é considerado **relevante** se o usuário o avaliou com `rating >= 4.0` no conjunto de teste.
