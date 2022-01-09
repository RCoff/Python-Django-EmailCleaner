web: gunicorn --chdir /app/gmailautocleaner gmailautocleaner.wsgi
celery: celery worker -A gmailautocleaner -l info