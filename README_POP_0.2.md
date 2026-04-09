# Avaliação do Motor CBF — Comparativo `cbf_df.csv` vs `cbf1.csv`

Métricas calculadas com **Mean Precision@K** e **Mean Recall@K** sobre o conjunto de teste, variando K em `[10, 20, 30, 40, 50, 100]`.

O motor usa TF-IDF + Similaridade de Cosseno com popularity bias (80/20).

## cbf_df.csv — Sem tags de usuários

| K | Mean Precision@K | Mean Recall@K | Usuários Avaliados |
|---|---|---|---|
| 10 | 0.0995 | 0.1136 | 608 |
| 20 | 0.0838 | 0.1802 | 608 |
| 30 | 0.0738 | 0.2306 | 608 |
| 40 | 0.0679 | 0.2773 | 608 |
| 50 | 0.0626 | 0.3110 | 608 |
| 100 | 0.0463 | 0.4239 | 608 |

## cbf1.csv — Com tags de usuários

| K | Mean Precision@K | Mean Recall@K | Usuários Avaliados |
|---|---|---|---|
| 10 | 0.1090 | 0.1117 | 608 |
| 20 | 0.0916 | 0.1829 | 608 |
| 30 | 0.0800 | 0.2344 | 608 |
| 40 | 0.0720 | 0.2743 | 608 |
| 50 | 0.0662 | 0.3114 | 608 |
| 100 | 0.0479 | 0.4263 | 608 |

## Comparativo direto

| K | Precision cbf | Precision cbf1 | Recall cbf | Recall cbf1 |
|---|---|---|---|---|
| 10 | 0.0995 | 0.1090 (+0.0095) | 0.1136 | 0.1117 (-0.0019) |
| 20 | 0.0838 | 0.0916 (+0.0078) | 0.1802 | 0.1829 (+0.0027) |
| 30 | 0.0738 | 0.0800 (+0.0062) | 0.2306 | 0.2344 (+0.0038) |
| 40 | 0.0679 | 0.0720 (+0.0041) | 0.2773 | 0.2743 (-0.0030) |
| 50 | 0.0626 | 0.0662 (+0.0036) | 0.3110 | 0.3114 (+0.0004) |
| 100 | 0.0463 | 0.0479 (+0.0016) | 0.4239 | 0.4263 (+0.0024) |

### Generalização — cbf_df.csv (Top 10 filmes mais recomendados, k=100)

| Posição | Movie ID | Título | Nº de Usuários |
|---|---|---|---|
| 1 | 780 | Independence Day (a.k.a. ID4) (1996) | 414 |
| 2 | 32 | Twelve Monkeys (a.k.a. 12 Monkeys) (1995) | 399 |
| 3 | 1 | Toy Story (1995) | 394 |
| 4 | 380 | True Lies (1994) | 384 |
| 5 | 165 | Die Hard: With a Vengeance (1995) | 375 |
| 6 | 110 | Braveheart (1995) | 362 |
| 7 | 1036 | Die Hard (1988) | 348 |
| 8 | 356 | Forrest Gump (1994) | 339 |
| 9 | 6 | Heat (1995) | 336 |
| 10 | 7153 | Lord of the Rings: The Return of the King, The (2003) | 334 |

### Generalização — cbf1.csv (Top 10 filmes mais recomendados, k=100)

| Posição | Movie ID | Título | Nº de Usuários |
|---|---|---|---|
| 1 | 32 | Twelve Monkeys (a.k.a. 12 Monkeys) (1995) | 464 |
| 2 | 79132 | Inception (2010) | 425 |
| 3 | 293 | Léon: The Professional (a.k.a. The Professional) (Léon) (1994) | 425 |
| 4 | 7153 | Lord of the Rings: The Return of the King, The (2003) | 403 |
| 5 | 260 | Star Wars: Episode IV - A New Hope (1977) | 403 |
| 6 | 2959 | Fight Club (1999) | 394 |
| 7 | 296 | Pulp Fiction (1994) | 385 |
| 8 | 780 | Independence Day (a.k.a. ID4) (1996) | 385 |
| 9 | 110 | Braveheart (1995) | 373 |
| 10 | 924 | 2001: A Space Odyssey (1968) | 372 |

## Notas sobre os datasets

- **cbf_df.csv**: enriquecido com dados da API TMDB — overview, tagline, keywords, cast (top 5), director. A coluna `geral` usa apenas campos textuais (exclui IDs e ratings numéricos).

- **cbf1.csv**: idem ao anterior, acrescido da coluna `tags` — agregação das tags inseridas pelos usuários do MovieLens (`tags.csv`), unidas com `|` por filme. Apenas **1.571 de 9.708** filmes possuem tags.
