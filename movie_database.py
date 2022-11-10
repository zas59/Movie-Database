'''This is a Flask app for a movie database. A user must log in to the site before viewing the movies. There is a hard-coded list of 3 movies
   that will be chosen at random to be displayed. Users can comment their reviews of the movies and see other users reviews as well.'''
import random
import os
import requests
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = Flask(__name__)

app.secret_key = 'abedisbatmannow'
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
app.config['USE_SESSION_FOR_NEXT'] = True

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)

class Review(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(5000), nullable=False)

    def __repr__(self) ->str:
        return f'{self.username} gives this movie a {self.rating}/10: {self.comment}'

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session['next'] = request.args.get('next')
    return render_template('login.html')

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/getloggedin', methods=['GET', 'POST'])
def getloggedin():
    form_data = request.form
    uname = form_data['username']

    user = User.query.filter_by(username=uname).first()
    if not user:
        return redirect(url_for('signup'))

    login_user(user)
    return redirect(url_for('home'))

    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    flash('Unrecognized username, please sign up below.')
    return render_template('signup.html')

@app.route('/getsignedup', methods=['GET', 'POST'])
def getsignedup():
    form_data = request.form
    uname = form_data['username']
    new_user = User(username = uname)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return 'You are logged out.'

@app.route('/handle_rating_form', methods = ['GET', 'POST'])
def handle_rating_form():
    form_data = request.form
    uname = current_user.username
    mov_id = form_data['MovieID']
    num_rating = int(form_data['rating'])
    mov_comment = form_data['review']

    new_review = Review(username = uname, movie_id =mov_id, rating=num_rating, comment=mov_comment)
    db.session.add(new_review)
    db.session.commit()

    return redirect(url_for('home'))



@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
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
    curr_mov_comments = Review.query.filter_by(movie_id = int(current_movie))

    return render_template('md.html', movie_title = movie_obj['title'],
     movie_tagline = movie_obj['tagline'], movie_genre_list = movie_genres,
     movie_img = movie_image, wiki_link = movie_wiki_link, movie_id = current_movie,
     all_comments = curr_mov_comments)

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

app.run(debug=True)
