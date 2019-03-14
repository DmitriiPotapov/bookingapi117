web: gunicorn --worker-class eventlet -w 1 app:app
init: python app.py db init
migrate: python app.py db migrate
upgrade: python app.py db upgrade
