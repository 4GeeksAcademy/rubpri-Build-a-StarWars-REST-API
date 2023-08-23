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
from models import db, User, People, Planets
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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def people_get():

    people_objects = People.query.all()
    serialized_people = [person.serialize() for person in people_objects]
    
    if serialized_people:
        return jsonify(serialized_people), 200
    else:
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
    else:
        return "Error", 400


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    
    planet = Planets.query.get(planet_id)

    if planet:
        return jsonify(planet.serialize()), 200
    return "Invalid Method", 404










# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
