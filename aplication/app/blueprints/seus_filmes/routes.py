from flask import request, render_template, redirect, url_for, Blueprint, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required


from app.extensions import db
from app.blueprints.seus_filmes.models import Movie, Rating


seus_filmes = Blueprint('seus_filmes',__name__,template_folder= 'templates')



@seus_filmes.route('/', methods=['GET'])
@login_required
def index():
    ratings = current_user.rating
    filmes = []

    for rating in ratings:
        filme = rating.movie

        title = filme.title
        poster_path = filme.poster_url
        id = filme.movieId

        filme = {
            "titulo": title,
            "poster_path":poster_path,
            "id": id
        }

        filmes.append(filme)
    
    return render_template('seus_filmes/seus_filmes.html', filmes=filmes)


@seus_filmes.route('/search_my_database')
@login_required
def search_my_database():
    query = request.args.get('q', '')
    if len(query) >= 2:
        # Filtra os filmes do SEU banco de dados que contêm a string da query
        # Assumindo que seu Model chama 'Filme' e tem a coluna 'titulo'
        filmes = Movie.query.filter(Movie.title.ilike(f'%{query}%')).limit(10).all()
        
        # Converte para uma lista de dicionários para o JSON
        results = [
            {'id': f.movieId, 'titulo': f.title, 'poster': f.year, 'ano': f.poster_url} 
            for f in filmes
        ]
        return jsonify(results)
    return jsonify([])


@seus_filmes.route('/movie/<int:rating_id>')
@login_required
def get_movie(movieId):
    pass
    
