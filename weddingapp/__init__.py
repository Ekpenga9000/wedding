from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from weddingapp import config

app = Flask(__name__,instance_relative_config=True)
app.config.from_pyfile('config.py')
app.config.from_object(config.LiveConfig)
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)

from weddingapp.routes import user_routes, admin_routes

from weddingapp import models,forms