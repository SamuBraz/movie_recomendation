from ...extensions import db



class Movie(db.Model):
    __tablename__ = 'Movie'  

    movieId = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    poster_url = db.Column(db.Integer, nullable=False)

    rating = db.relationship('Rating', back_populates='movie')
    movie_genre = db.relationship('MovieGenre', back_populates='movie')


    def __repr__(self):
        return f"{self.title}: {self.poster_url}"
    
    def get_id(self):
        return self.movieId
    

class Rating(db.Model):
    __tablename__ = 'Rating'
    
    # Chaves Estrangeiras que também compõem uma Chave Primária Composta
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    movieId = db.Column(db.Integer, db.ForeignKey('Movie.movieId'))


    rating_id = db.Column(db.Integer, primary_key=True)
    # O campo extra que você mencionou
    rating = db.Column(db.Integer, nullable=False)

    # Back-references para facilitar a navegação entre objetos
    user = db.relationship('User', back_populates='ratings')
    movie = db.relationship('Movie', back_populates='ratings')


class Genre(db.Model):
    __tablename__ = 'Genre'

    nome_genres = db.Column(db.String, nullable=False)
    genres_id = db.Column(db.Integer, primary_key=True)


    movie_genre = db.relationship('MovieGenre', back_populates='genre')


class MovieGenre(db.Model):
    __tablename__ = 'MovieGenre'

    genres_id = db.Column(db.Integer, db.ForeignKey('Genre.genres_id'), primary_key=True)
    movieId = db.Column(db.Integer, db.ForeignKey('Movie.movieId'), primary_key=True)

    movie = db.relationship('Movie', back_populates='movieGenre')
    genre = db.relationship('Genre', back_populates='movieGenre')
    


    

    

    