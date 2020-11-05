import os
import os.path
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
    GET /drinks
        it should be a public endpoint 
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
# No need for permissions since anyone can see the available short detailed drinks (Udacity's students)
def get_drinks():
    try:
        # Get all the drinks from the database
        drinks = Drink.query.all()

        # Return a status code 200 and json of drinks list and set the success message to true
        return jsonify({
            'success': True,
            # Return the retrieved drinks in the drink.short() data representation
            'drinks': [d.short() for d in drinks]
        }), 200
    except:
        # If the server encountered an unexpected error, raise 500 status code (500 Internal Server Error)
        abort(500)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
# Require the 'get:drinks-detail' permission
@requires_auth('get:drinks-detail')
# Because of calling the 'requires_auth', we need to take the payload as it returns it
def get_drinks_detail(payload):
    try:
        # Get all the drinks from the database
        drinks = Drink.query.all()

        # Return a status code 200 and json of drinks list and set the success message to true
        return jsonify({
            'success': True,
            # Return the retrieved drinks in the drink.long() data representation 
            # for the Barista and Manager to see the details of the drinks (recipe)
            'drinks': [d.long() for d in drinks]
        }), 200
    except:
        # If the server encountered an unexpected error, raise 500 status code (500 Internal Server Error)
        abort(500)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
# Require the 'post:drinks' permission
@requires_auth('post:drinks')
# Because of calling the 'requires_auth', we need to take the payload as it returns it
def add_drink(payload):
    # Get the form's data from the request 
    # I added the 'force=True' because of this error: TypeError: 'NoneType' object is not callable
    # (Reference: https://stackoverflow.com/questions/20001229/how-to-get-posted-json-in-flask)
    body = request.get_json(force=True)

    # Check if the json keys exist
    if ('title' not in body) or ('recipe' not in body):
        # If both keys are missing, send an error (unprocessable - 422)
        abort(422)

    # Check if the title and recipe aren't missing
    if (body['title'] is None) or (body['recipe'] is None):
        # If fields are missing, send an error (unprocessable - 422)
        abort(422)
    
    title = body['title']
    recipe = body['recipe']

    """
    According to (drink-form.component.html) Ingredient Name, Number of Parts, and Color must be filled.
    Before looping the ingredients, we must make sure that the recipe is a list (if it has one ingredient
         it will be a string and this error will occur: TypeError: string indices must be integers).
    """
    # Check if each ingredient in the recipe contains the drink.long() data representation
    if isinstance(recipe, list):
        for ingredient in recipe:
            if (ingredient['name'] is None) or (ingredient['parts'] is None) or (ingredient['color'] is None):
                # If fields are missing, send an error (unprocessable - 422)
                abort(422)
    else:
        if (recipe['name'] is None) or (recipe['parts'] is None) or (recipe['color'] is None):
            # If fields are missing, send an error (unprocessable - 422)
            abort(422)
    
    # Convert the recipe list to a String using (json.dumps) to insert it into the database
    # (Reference: https://docs.python.org/3/library/json.html)
    recipe = json.dumps(recipe)

    try:
        # Create an instance of the Drink model with the form's data
        new_drink = Drink(title=title, recipe=recipe)
        # Insert the new drink into the database
        new_drink.insert()

        # Return a status code 200 and json of drinks list and set the success message to true
        return jsonify({
            'success': True,
            # Return the drink which is an array containing only the newly created drink in the drink.long() data representation
            # for the Barista and Manager to see the details of the drinks (recipe)
            'drinks': [new_drink.long()]
        }), 200
    
    except:
        # If an error occured while proccessing the INSERT, send an error (unprocessable - 422)
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
# Require the 'patch:drinks' permission
@requires_auth('patch:drinks')
# Because of calling the 'requires_auth', we need to take the payload as it returns it
def update_drink(payload, id):
    # Retrieve the specified drink from the database by its ID
    drink = Drink.query.get(id)
    # Check if the drink exists in the database


        # If the drink doesn't exist, send an error (not found - 404)
if drink is None:
    return json.dumps({
        'success':
        False,
        'error':
        'Drink #' + id + ' not found to be edited'
            }), 404

    # Get the form's data from the request
    # I added the 'force=True' because of this error: TypeError: 'NoneType' object is not callable
    # (Reference: https://stackoverflow.com/questions/20001229/how-to-get-posted-json-in-flask)
    body = request.get_json(force=True)

    # Check if the json keys exist
    if ('title' not in body) and ('recipe' not in body):
        # If both keys are missing, send an error (unprocessable - 422)
        abort(422)

    # Check if both, the title and recipe, are missing
    if (body['title'] is None) and (body['recipe'] is None):
        # If both fields are missing, send an error (unprocessable - 422)
        abort(422)

    # Check the user's updated fields and assign them to variables (if exists)
    if 'title' in body:
        title = body['title']
        # Assign the new title to the old drink's title
        drink.title = title

    if 'recipe' in body:
        recipe = body['recipe']
        """
        According to (drink-form.component.html) Ingredient Name, Number of Parts, and Color must be filled.
        Before looping the ingredients, we must make sure that the recipe is a list (if it has one ingredient
            it will be a string and this error will occur: TypeError: string indices must be integers).
        """
        # Check if each ingredient in the recipe contains the drink.long() data representation
        if isinstance(recipe, list):
            for ingredient in recipe:
                if (ingredient['name'] is None) or (ingredient['parts'] is None) or (ingredient['color'] is None):
                    # If fields are missing, send an error (unprocessable - 422)
                    abort(422)
        else:
            if (recipe['name'] is None) or (recipe['parts'] is None) or (recipe['color'] is None):
                # If fields are missing, send an error (unprocessable - 422)
                abort(422)

        # Convert the recipe list to a String using (json.dumps) to insert it into the database
        # (Reference: https://docs.python.org/3/library/json.html)
        recipe = json.dumps(recipe)
        # Assign the new recipe to the old drink's recipe
        drink.recipe = recipe

    try:
        # Update the drink data
        drink.update()

        # Return a status code 200 and json of drinks list and set the success message to true
        return jsonify({
            'success': True,
            # Return the drink which is an array containing only the updated drink in the drink.long() data representation
            # for the Barista and Manager to see the details of the drinks (recipe)
            'drinks': [drink.long()]
        }), 200

    except:
        # If an error occured while proccessing the UPDATE, send an error (unprocessable - 422)
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
# Require the 'delete:drinks' permission
@requires_auth('delete:drinks')
# Because of calling the 'requires_auth', we need to take the payload as it returns it
def delete_drink(payload, id):
    # Retrieve the specified drink from the database by its ID
    drink = Drink.query.get(id)
    # Check if the drink exists in the database
    if not drink:
        # If the drink doesn't exist, send an error (not found - 404)
        abort(404)

    try:
        # Delete the drink from the database
        drink.delete()

        # Return a status code 200 and json of drinks list and set the success message to true
        return jsonify({
            'success': True,
            # Return the deleted drink's id
            'delete': id
        }), 200

    except:
        # If an error occured while proccessing the UPDATE, send an error (unprocessable - 422)
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
# Error Handler for (404 - Not Found)
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource Not Found'
    }), 404

# Error Handler for (400 - Bad Request)
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400

# Error Handler for (500 - Internal Server Error)
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500

# Error Handler for (405 - Method Not Allowed)
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
        'success': False,
        'error': e.status_code,
        'message': e.error['description']
    }), e.status_code
    
