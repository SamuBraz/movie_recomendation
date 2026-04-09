# Avaliação do Motor CBF — Comparativo `cbf_df.csv` vs `cbf1.csv`

Métricas calculadas com **Mean Precision@K** e **Mean Recall@K** sobre o conjunto de teste, variando K em `[10, 20, 30, 40, 50, 100]`.

O motor usa TF-IDF + Similaridade de Cosseno com popularity bias (80/20).

## cbf_df.csv — Sem tags de usuários

| K | Mean Precision@K | Mean Recall@K | Usuários Avaliados |
|---|---|---|---|
| 10 | 0.0382 | 0.0431 | 608 |
| 20 | 0.0328 | 0.0663 | 608 |
| 30 | 0.0303 | 0.0854 | 608 |
| 40 | 0.0288 | 0.1022 | 608 |
| 50 | 0.0271 | 0.1175 | 608 |
| 100 | 0.0223 | 0.1825 | 608 |

## cbf1.csv — Com tags de usuários

| K | Mean Precision@K | Mean Recall@K | Usuários Avaliados |
|---|---|---|---|
| 10 | 0.0544 | 0.0564 | 608 |
| 20 | 0.0432 | 0.0831 | 608 |
| 30 | 0.0393 | 0.1061 | 608 |
| 40 | 0.0361 | 0.1247 | 608 |
| 50 | 0.0337 | 0.1407 | 608 |
| 100 | 0.0260 | 0.2061 | 608 |

## Comparativo direto

| K | Precision cbf | Precision cbf1 | Recall cbf | Recall cbf1 |
|---|---|---|---|---|
| 10 | 0.0382 | 0.0544 (+0.0163) | 0.0431 | 0.0564 (+0.0133) |
| 20 | 0.0328 | 0.0432 (+0.0104) | 0.0663 | 0.0831 (+0.0168) |
| 30 | 0.0303 | 0.0393 (+0.0090) | 0.0854 | 0.1061 (+0.0207) |
| 40 | 0.0288 | 0.0361 (+0.0074) | 0.1022 | 0.1247 (+0.0225) |
| 50 | 0.0271 | 0.0337 (+0.0066) | 0.1175 | 0.1407 (+0.0231) |
| 100 | 0.0223 | 0.0260 (+0.0037) | 0.1825 | 0.2061 (+0.0236) |

### Generalização — cbf_df.csv (Top 10 filmes mais recomendados, k=100)

| Posição | Movie ID | Título | Nº de Usuários |
|---|---|---|---|
| 1 | 26849 | Stand, The (1994) | 457 |
| 2 | 26887 | Langoliers, The (1995) | 408 |
| 3 | 27036 | Merlin (1998) | 323 |
| 4 | 52281 | Grindhouse (2007) | 305 |
| 5 | 126430 | The Pacific (2010) | 256 |
| 6 | 198 | Strange Days (1995) | 252 |
| 7 | 130842 | Power/Rangers (2015) | 250 |
| 8 | 63433 | Farscape: The Peacekeeper Wars (2004) | 245 |
| 9 | 99764 | It's Such a Beautiful Day (2012) | 242 |
| 10 | 26614 | Bourne Identity, The (1988) | 238 |

### Generalização — cbf1.csv (Top 10 filmes mais recomendados, k=100)

| Posição | Movie ID | Título | Nº de Usuários |
|---|---|---|---|
| 1 | 26849 | Stand, The (1994) | 464 |
| 2 | 26887 | Langoliers, The (1995) | 430 |
| 3 | 52281 | Grindhouse (2007) | 326 |
| 4 | 27036 | Merlin (1998) | 304 |
| 5 | 130842 | Power/Rangers (2015) | 271 |
| 6 | 7842 | Dune (2000) | 268 |
| 7 | 63433 | Farscape: The Peacekeeper Wars (2004) | 257 |
| 8 | 106642 | Day of the Doctor, The (2013) | 246 |
| 9 | 2851 | Saturn 3 (1980) | 245 |
| 10 | 62970 | Tin Man (2007) | 241 |

## Notas sobre os datasets

- **cbf_df.csv**: enriquecido com dados da API TMDB — overview, tagline, keywords, cast (top 5), director. A coluna `geral` usa apenas campos textuais (exclui IDs e ratings numéricos).

- **cbf1.csv**: idem ao anterior, acrescido da coluna `tags` — agregação das tags inseridas pelos usuários do MovieLens (`tags.csv`), unidas com `|` por filme. Apenas **1.571 de 9.708** filmes possuem tags.
