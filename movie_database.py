'''This is a basic Flask app for a movie database. There is a hard-coded list of 3 movies
   that will be chosen at random to be displayed.'''
import random
import os
import requests
import psycopg2
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
secret_key = "../.ssh/terraform"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500), nullable=False)

    def __repr__(self) ->str:
        return f'{self.username} gives this movie a {self.rating}/10: {self.comment}'

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    '''Base function that runs evry time web page is refreshed.
       Gets TMDB json object for a movie and calls necessary functions for other info.'''
    movie_list = ['8193', '20352', '346364']
    current_movie = str(random.choice(movie_list))
    TMDB_LINK = 'https://api.themoviedb.org/3/movie/'
    TMDB_MOVIE_REQUEST = TMDB_LINK + current_movie
    api_key = os.getenv('TMDB_API_KEY')
    response = requests.get(
        TMDB_MOVIE_REQUEST,
        params={
            'api_key': api_key
        }
    )
    json_data = response.json()
    movie_obj = json_data

    movie_wiki_link = get_wiki_link(movie_obj)
    movie_image = get_movie_image(current_movie, movie_list)
    movie_genres = get_movie_genres(movie_obj)
    curr_movie_reviews = get_reviews(current_movie)

    return render_template('md.html', movie_title = movie_obj['title'],
     movie_tagline = movie_obj['tagline'], movie_genre_list = movie_genres,
     movie_img = movie_image, wiki_link = movie_wiki_link, movie_id = current_movie,
     movie_reviews = curr_movie_reviews)

def get_wiki_link(movie_obj):
    '''Takes in movie object and returns the wiki link for that movie.'''
    wiki_search = movie_obj['title'] + ' film'
    WIKI_REQUEST = 'https://en.wikipedia.org/w/api.php'
    wiki_response = requests.get(
        WIKI_REQUEST,
        params={
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': wiki_search
        }
    )
    wiki_json_data = wiki_response.json()
    wiki_obj = wiki_json_data
    wiki_page_id = str(wiki_obj['query']['search'][0]['pageid'])
    movie_wiki_link = 'https://en.wikipedia.org/?curid=' + wiki_page_id
    return movie_wiki_link

def get_movie_image(current_movie, movie_list):
    '''Takes in the current movie id as well as the list of movies
       and returns the image source for the current movie.'''
    movie_image = ''
    movie_images = ['https://upload.wikimedia.org/wikipedia/en/8/87/Napoleon_dynamite_post.jpg',
        'https://upload.wikimedia.org/wikipedia/en/c/c0/Despicable_Me_%282010_animated_feature_film%29.jpg',
        'https://upload.wikimedia.org/wikipedia/en/5/5a/It_%282017%29_poster.jpg']
    if current_movie == movie_list[0]:
        movie_image = movie_images[0]
    elif current_movie == movie_list[1]:
        movie_image = movie_images[1]
    else:
        movie_image = movie_images[2]
    return movie_image

def get_movie_genres(movie_obj):
    '''Takes in the current movie object and returns the list of genres for that movie.'''
    movie_genres = 'Genres: '
    genre_count = 0
    for genre in movie_obj['genres']:
        genre_count += 1
    genre_counter = 0
    for genre in range(0, genre_count):
        movie_genres += movie_obj['genres'][genre]['name']
        genre_counter +=1
        if genre_counter != genre_count:
            movie_genres += ', '
    return movie_genres

def get_reviews(current_movie):
    current_movie = int(current_movie)
    reviews = Review.query.filter_by(movie_id = current_movie)
    all_reviews = str(repr(reviews))
    return all_reviews

app.run(debug=True)
