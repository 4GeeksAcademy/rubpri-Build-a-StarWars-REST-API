"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def people_get():

    people_objects = People.query.all()
    serialized_people = [person.serialize() for person in people_objects]
    
    if serialized_people:
        return jsonify(serialized_people), 200
    return "Error", 400
     

@app.route('/people/<int:person_id>', methods=['GET'])
def get_single_person(person_id):
    
    person = People.query.get(person_id)

    if person:
        return jsonify(person.serialize()), 200
    return "Invalid Method", 404


@app.route('/planets', methods=['GET'])
def planets_get():

    planets_objects = Planets.query.all()
    serialized_planets = [planet.serialize() for planet in planets_objects]
    
    if serialized_planets:
        return jsonify(serialized_planets), 200
    return "Error", 404


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    
    planet = Planets.query.get(planet_id)

    if planet:
        return jsonify(planet.serialize()), 200
    return "Invalid Method", 404

@app.route('/users', methods=['GET'])
def users_get():

    all_users = User.query.all()
    serialized_users = [user.serialize() for user in all_users]

    if serialized_users:
        return jsonify(serialized_users), 200
    return "Error", 404

@app.route('/users/favorites/<int:id>', methods=['GET'])
def users_favorites(id):
    
    favorites = db.session.execute(db.select(Favorites).where(Favorites.user_id == id)).scalars()

    results = [item.serialize() for item in favorites]
    
    if results:
        return jsonify(results), 200

    else:
        return "Error", 404




# [POST] /favorite/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el planet id = planet_id


@app.route('/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def favorite_planet_post(user_id, planet_id):

    user = User.query.get_or_404(user_id)
    user_add = user.id
    

    planet = Planets.query.get_or_404(planet_id)
    planet_add = planet.id
    

    new_favorite = Favorites(
    planets_id=planet_add,
    user_id=user_add
    )

    db.session.add(new_favorite)
    db.session.commit()

    response_body = {
        "message": "New favorite added",
        "status": "ok",
        "new_favorite": new_favorite.serialize()
    }
        
    return response_body, 200











# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
