#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import enum
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_artists = db.Column(db.String(6), default=False, nullable=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows_booked = db.relationship('Show', backref='venueShow', lazy=True)


artist_genre = db.Table('artist_genre',
                        db.Column('artist_id', db.Integer, db.ForeignKey(
                            'Artist.id'), primary_key=True),
                        db.Column('genre_id', db.Integer, db.ForeignKey(
                            'Genre.id'), primary_key=True)
                        )


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.String(6), default=False, nullable=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows_booked = db.relationship('Show', backref='artistShow', lazy=True)
    genres = db.relationship('Genre', secondary=artist_genre,
                             backref=db.backref('genres', lazy=True))


class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(30))


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    show_time = db.Column(db.DateTime, nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
    venues = Venue.query.all()
    areas = Venue.query.order_by(Venue.state)
    return render_template('pages/venues.html', venues=venues, areas=areas)

#  Search Venues
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
    keyword = request.form.get('search_term')
    search_term = '%{0}%'.format(keyword)
    response = Venue.query.filter(Venue.name.ilike(search_term))
    count = response.count()
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''), count=count)

#  Show Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    return render_template('pages/show_venue.html', venue=venue)


#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    address = request.form.get('address', '')
    phone = request.form.get('phone', '')
    genres = request.form.get('genres', '')
    facebook_link = request.form.get('facebook_link', '')
    website_link = request.form.get('website_link', '')
    seeking_artists = request.form.get('seeking_artists', '')
    seeking_description = request.form.get('seeking_description', '')
    image_link = request.form.get('image_link', '')

    venue = Venue(name=name, city=city, state=state, phone=phone,
                  address=address, genres=genres, facebook_link=facebook_link,
                  website_link=website_link, seeking_artists=seeking_artists,
                  seeking_description=seeking_description, image_link=image_link)

    try:
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('index'))
    except:
        db.session.rollback()
        flash('Venue was not listed!')
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Delete Venue
#  ----------------------------------------------------------------
@app.route("/venues/<int:venue_id>/delete", methods=['POST'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Your venue has been deleted!', 'success')
        return redirect(url_for('index'))
    except:
        db.session.rollback()
        flash('There was a problem with this request!', 'warning')
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


#  Search Artists
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
    keyword = request.form.get('search_term')
    search_term = '%{0}%'.format(keyword)
    response = Artist.query.filter(Artist.name.ilike(search_term))
    count = response.count()
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''), count=count)


#  Show Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.get(artist_id)
    return render_template('pages/show_artist.html', artist=data)


#  Delete Artist
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/delete", methods=['POST'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
        flash('Your artist has been deleted!', 'success')
        return redirect(url_for('index'))
    except:
        db.session.rollback()
        flash('There was a problem with this request!', 'warning')
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Update Artist - Populating the form with data
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    data = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=data)

#  Update Artist - Writing new data to the database
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link', '')
    website_link = request.form.get('website_link', '')
    seeking_venue = request.form.get('seeking_venue', '')
    seeking_description = request.form.get('seeking_description', '')
    image_link = request.form.get('image_link', '')

    newArtist = Artist(name=name, city=city, state=state, phone=phone,
                       facebook_link=facebook_link, website_link=website_link,
                       seeking_venue=seeking_venue, seeking_description=seeking_description,
                       image_link=image_link)

    choices = Genre.query.all()

    try:

        artist = Artist.query.get(artist_id)
        for genre in genres:
            genre = Genre(genre=genre)
            for choice in choices:
                if genre.genre == choice.genre:
                    artist.genres.append(choice)
                    break

        artist.name = newArtist.name
        artist.city = newArtist.city
        artist.state = newArtist.state
        artist.phone = newArtist.phone
        artist.facebook_link = newArtist.facebook_link
        artist.website_link = newArtist.website_link
        artist.seeking_venue = newArtist.seeking_venue
        artist.seeking_description = newArtist.seeking_description
        artist.image_link = newArtist.image_link
        db.session.commit()
        flash('Artist was successfully modified ')
    except:
        db.session.rollback()
        flash('Artist was not modified!')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

#  Update Venue - Populating the form with data
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    data = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=data)

#  Update Venue - Writing new data to the database
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    address = request.form.get('address', '')
    phone = request.form.get('phone', '')
    genres = request.form.get('genres', '')
    facebook_link = request.form.get('facebook_link', '')
    website_link = request.form.get('website_link', '')
    seeking_artists = request.form.get('seeking_artists', '')
    seeking_description = request.form.get('seeking_description', '')
    image_link = request.form.get('image_link', '')

    newVenue = Venue(name=name, city=city, state=state, phone=phone,
                     genres=genres, facebook_link=facebook_link, website_link=website_link,
                     seeking_artists=seeking_artists, seeking_description=seeking_description,
                     image_link=image_link)

    try:
        venue = Venue.query.get(venue_id)
        venue.name = newVenue.name
        venue.city = newVenue.city
        venue.state = newVenue.state
        venue.phone = newVenue.phone
        venue.genres = newVenue.genres
        venue.facebook_link = newVenue.facebook_link
        venue.website_link = newVenue.website_link
        venue.seeking_artists = newVenue.seeking_artists
        venue.seeking_description = newVenue.seeking_description
        venue.image_link = newVenue.image_link
        db.session.commit()
        flash('Venue was successfully modified ')
    except:
        db.session.rollback()
        flash('Venue was not modified!')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link', '')
    website_link = request.form.get('website_link', '')
    seeking_venue = request.form.get('seeking_venue', '')
    seeking_description = request.form.get('seeking_description', '')
    image_link = request.form.get('image_link', '')

    artist = Artist(name=name, city=city, state=state, phone=phone,
                    facebook_link=facebook_link, website_link=website_link, seeking_venue=seeking_venue,
                    seeking_description=seeking_description, image_link=image_link)

    choices = Genre.query.all()

    try:
        for genre in genres:
            genre = Genre(genre=genre)
            for choice in choices:
                if genre.genre == choice.genre:
                    artist.genres.append(choice)
                    break

        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + name + ' was successfully listed!')
        return redirect(url_for('index'))
    except:
        db.session.rollback()
        flash('Artist was not listed!')
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    shows = Show.query.all()
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    return render_template('pages/shows.html', shows=shows)


#  Create Show
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    artist_id = request.form.get('artist_id', '')
    venue_id = request.form.get('venue_id', '')
    start_time = request.form.get('start_time', '')

    show = Show(artist_id=artist_id, venue_id=venue_id, show_time=start_time)
    try:
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('Show was not listed!')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
