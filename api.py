from flask import request, Response
from config import db, app
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

    planets_hash = {}

    for planet in result['results']:
        planet_name = slugify(planet['name'])
        apparitions = len(planet['films'])
        planets_hash.setdefault(planet_name, apparitions)

    return planets_hash


@app.route("/get-planets", methods=['GET'])
def get_all_planets():
    try:
        planet_id = request.args.get('id')
        planet_name = request.args.get('name')

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

        return Response(dumps({'planets': result}), status=200, mimetype='application/json')
    except Exception as e:
        return Response(dumps({'error': str(e)}), status=500, mimetype='application/json')


@app.route("/add-planet", methods=['POST'])
def add_planet():
    try:
        data = json.loads(request.data)
        try:
            planet_name = data['name']
            planet_climate = data['climate']
            planet_terrain = data['terrain']
        except Exception:
            return Response(dumps({'error': 'Preencha todos os campos!'}), status=422, mimetype='application/json')

        status = db.Planets.insert_one({
            "name": planet_name,
            "climate": planet_climate,
            "terrain": planet_terrain
        })

        return Response(dumps({'message': 'Success'}), status=201, mimetype='application/json')
    except Exception as e:
        return Response(dumps({'error': str(e)}), status=500, mimetype='application/json')


@app.route("/delete-planet/<planet_id>", methods=['DELETE'])
def delete_planet(planet_id):
    try:
        delete_planet = db.Planets.delete_one({"_id": ObjectId(planet_id)})
        if delete_planet.deleted_count > 0:
            return Response(status=204, mimetype='application/json')
        else:
            return Response(dumps({'message': 'Planeta não encontrado'}), status=404, mimetype='application/json')
    except Exception as e:
        return Response(dumps({'error': str(e)}), status=500, mimetype='application/json')
