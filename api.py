from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
import json
import requests
import dpath.util
from cachetools import cached, TTLCache
from slugify import slugify
import re

# setting cache time to 5 minutes
cache = TTLCache(maxsize=100, ttl=300)

client = MongoClient('localhost:27017')
db = client.PlanetDB

app = Flask(__name__)


def _request(url=None):
    if not url:
        url = 'https://swapi.co/api/planets/'
    planets = requests.get(url)
    planets = planets.json()
    return planets


@cached(cache)
def get_planets_swapi():
    planets = _request()
    result = planets

    try:
        while planets['next']:
            planets = _request(planets['next'])
            dpath.util.merge(result, planets)
    except Exception as e:
        raise Exception(e)
        pass

    planets_hash = {}

    for planet in result['results']:
        planet_name = slugify(planet['name'])
        apparitions = len(planet['films'])
        planets_hash.setdefault(planet_name, apparitions)

    return planets_hash


@app.route("/get_all_planets", methods=['GET'])
def get_all_planets():
    try:
        planet_id = request.args.get('id')
        planet_name = request.args.get('name')

        print(planet_name)
        print(planet_id)

        if planet_id:
            planets = db.Planets.find({"_id": ObjectId(planet_id)})
        elif planet_name:
            planets = db.Planets.find({"name": re.compile(planet_name, re.IGNORECASE)})
        else:
            planets = db.Planets.find()
        result = []
        get_hash_planets = get_planets_swapi()
        for planet in planets:
            total_apparitions = 0
            obs = ''
            slug_name = slugify(planet['name'])

            try:
                total_apparitions = get_hash_planets[slug_name]
            except KeyError:
                obs = 'Planet not found in swapi!'
                pass

            result.append({
                'id': planet['_id'],
                'name': planet['name'],
                'climate': planet['climate'],
                'terrain': planet['terrain'],
                'total_apparitions': total_apparitions,
                'obs': obs
            })

        return dumps({'planets': result})
    except Exception as e:
        return dumps({'error': str(e)})


@app.route("/add_planet", methods=['POST'])
def add_planet():
    try:
        data = json.loads(request.data)

        planet_name = data['name']
        planet_climate = data['climate']
        planet_terrain = data['terrain']

        validated = planet_name and planet_climate and planet_terrain

        if validated:
            status = db.Planets.insert_one({
                "name": planet_name,
                "climate": planet_climate,
                "terrain": planet_terrain
            })
        return dumps({'message': 'SUCCESS'})
    except Exception as e:
        return dumps({'error': str(e)})


@app.route("/delete-planet/<planet_id>", methods=['DELETE'])
def delete_planet(planet_id):
    try:
        delete_planet = db.Planets.delete_one({"_id": ObjectId(planet_id)})
        if delete_planet.deleted_count > 0:
            return dumps({'message': 'SUCCESS'}), 204
        else:
            return dumps({'message': 'Planeta não encontrado'}), 404
    except Exception as e:
        return dumps({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
