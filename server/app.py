from flask import Flask
from flask_session import Session  
import redis
from celery import Celery
import os
EXPIRES_IN = 50*60

PORT = 5000

TEMPLATE_DIR = os.path.abspath('./box-collab/dist')
STATIC_DIR = os.path.abspath('./box-collab/dist/assets')
app = Flask(__name__,  template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Configure session to use filesystem (or you can use Redis, MongoDB, etc.)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_default_dev_key')
app.config['SESSION_TYPE'] = 'filesystem'  # Options: 'redis', 'mongodb', 'sqlalchemy', etc.
app.config['SESSION_PERMANENT'] = False    # Optional: False means session expires when browser closes
app.config['SESSION_USE_SIGNER'] = True    # Optional: adds extra protection by signing session data
Session(app)  # <-- Initiali

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name,
                broker=app.config['CELERY_BROKER_URL'],
                backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)


