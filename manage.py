from app import create_app
from flask_script import Manager
import os
from app.models import Role,User

from app.models import User
from app import db

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
manager=Manager(app)

if __name__ == '__main__':
    manager.run()