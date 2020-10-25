#Import Libs
from .models import URL
from . import url
from flask import request, url_for, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from directory.utils.random_letter import gen_random_letter
from directory.apps import db
from sqlalchemy.exc import IntegrityError

#Set route for shrink url view
@url.route('/', methods=['POST'])
@jwt_required
def shrink_url():
    #Get url from JSON request
    url_json = request.get_json()

    #Get username from jwt token identity
    username = get_jwt_identity()

    #Generate random letters
    short_url = url_for('index', url=gen_random_letter(), _external=True)

    #Add to database
    url = URL()
    url.original_url = url_json['url']
    url.short_url = short_url
    url.username = username
    db.session.add(url)
    db.session.commit()

    #Return shrinked url
    return jsonify({"original_url": f"{url_json['url']}", "shrinked_url": f"{short_url}"}), 200

@url.route('/', methods=['GET'])
@jwt_required
def preview_url():
    #Get url from request
    url_json = request.get_json()

    #Search for url in database
    url = URL.query.filter(URL.short_url.ilike(url_json['url'])).first()

    if not url:
        return {'error': 'url not found.'}, 404
    
    #Return original url
    return {'original_url': f'{url.original_url}'}, 200