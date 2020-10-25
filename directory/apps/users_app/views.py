#Import Libs
from datetime import timedelta

from directory.apps import db, jwt_manager, token_container
from directory.apps.url_app.models import URL
from flask import jsonify, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jti, get_jwt_identity, get_raw_jwt,
                                jwt_refresh_token_required, jwt_required)
from sqlalchemy.exc import IntegrityError

from . import users
from .models import User


#Create function to check for blacklisted tokens
@jwt_manager.token_in_blacklist_loader
def revoke_check(decrypted_token):
    #Get token identity (username)
    token_redis = decrypted_token['identity']
    entry = token_container.get(f"{token_redis}_refresh")
    #Check if the token exists in redis database
    if entry is None:
        return True
    return False

#Set route for users register view
@users.route('/', methods=['POST'])
def users_register():
    #Get user JSON data from request and validate them
    try:
        user_json = request.get_json()
        username = user_json['username']
        email = user_json['email']
        password = user_json['password']
    except KeyError:
        return {"error": "Invalid Request. Check the docs."}, 400

    #create user in database
    try:
        new_user = User()
        try:
            new_user.username = username
        except ValueError as error:
            return {"error": f"{error}"}, 400
        new_user.email = email
        try:
            new_user.password = password
        except ValueError as error:
            return {"error": f"{error}"}, 400
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User created successfully!"}, 201
    #Check if user exists
    except IntegrityError:
        db.session.rollback()
        return {"error": "User exists."}, 400
    
#Set route for user login view
@users.route('/login/', methods=['POST'])
def users_login():
    #Get user login data from request in JSON
    user_json = request.get_json()

    #Check and validate the data
    try:
        user = User.query.filter(User.username.ilike(user_json['username'])).first()
        password = user_json['password']
    except KeyError:
        return {"error": "Invalid request body data."}, 400

    #Check if user exists
    if not user:
        return {"error": "User does not exist."}, 404
    
    #Check if the user is already logged in
    if token_container.get(f"{user.username}_access") or token_container.get(f"{user.username}_refresh"):
        refresh_token = token_container.get(f"{user.username}_refresh")
        return jsonify({'msg': 'You are already logged in. If you want to get new access token, read the docs and use the refresh token.', 'refresh_token': f'{refresh_token}'})
    #Check the password
    if not User.check_password(user.password, password):
        return {"error": "Incorrect password."}, 401

    #Generate an access token for authentication
    access_token = create_access_token(identity=(user.username), fresh=True)
    #Generate refresh token for access token expiration backup
    refresh_token = create_refresh_token(identity=(user.username), expires_delta=timedelta(days=30))
    #Add generated tokens to redis database
    token_container.set(f"{user.username}_access", access_token, timedelta(minutes=15))
    token_container.set(f"{user.username}_refresh", refresh_token, timedelta(days=30))

    #return token data as JSON on login
    return {"access_token": f"{access_token}", "refresh_token": f"{refresh_token}"}, 200

#Set route for users index view
@users.route('/', methods=['GET'])
@jwt_required
def users_index():
    #Get the username from authentication token identity
    username = get_jwt_identity()
    #Find the user in database
    user = User.query.filter(User.username.ilike(username)).first()

    #Return the user data as JSON
    return {"username": f"{user.username}", "email": f"{user.email}"}

#Set route for edit user view
@users.route('/', methods=['PUT'])
@jwt_required
def users_edit():
    #Get new user data from request
    user = request.get_json()
    try:
        username = user['username']
        email = user['email']
        password = user['password']
    except KeyError:
        return {"error": "Invalid Request. Please Check the docs."}, 400

    #Make changes in database
    user = User.query.filter(User.username.ilike(get_jwt_identity())).first()
    try:
        user.username = username
        user.email = email
        user.password = password
        db.session.commit()
        return {"message": "User info edited successfully!"}, 200
    except IntegrityError:
        db.session.rollback()
        return {"error": "Another user with these credentials exists!"}, 400

#Set route for users logout view
@users.route('/', methods=['DELETE'])
@jwt_required
def users_logout():
    #Get username from token
    username = get_jwt_identity()
    #Remove tokens from redis
    token_container.delete(f"{username}_access")
    token_container.delete(f"{username}_refresh")

    return {'msg': 'Logged out successfully!'}, 200

#Set route for refresh token view
@users.route('/new_token/', methods=['PUT'])
@jwt_refresh_token_required
def refresh_token():
    #Remove the previous jwt access token
    token_container.delete(f"{get_jwt_identity()}_access")
    #Generate new access token
    access_token = create_access_token(identity=(get_jwt_identity()), fresh=False)
    #Add generated token to redis database
    token_container.set(f"{get_jwt_identity()}_access", access_token)
    #Return the generated access token
    return {"access_token": f"{access_token}"}, 205

#Set route for get links view
@users.route('/links/', methods=['GET'])
@jwt_required
def users_get_links():
    #Get username from jwt identity
    username = get_jwt_identity()
    #Get a list of links from current user in database
    links = URL.query.filter(URL.username.ilike(username)).all()
    if not links:
        return {'message': 'nothing found'}, 404
    #Define a dictionary and add items to it
    link_list = {}
    for link in links:
        link_list[link.original_url] = link.short_url
    
    #Return the JSON format of dictionary
    return jsonify(link_list), 200
