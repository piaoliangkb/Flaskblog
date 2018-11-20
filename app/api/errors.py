from flask import jsonify


def forbidden(message):
    response = jsonify({'error': 'forbieedn', 'message': message})
    response.status_code = 403
    return response
