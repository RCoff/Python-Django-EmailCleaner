web: gunicorn --chdir /app/gmailautocleaner gmailautocleaner.wsgi
celery: celery -A gmailautocleaner worker -l info