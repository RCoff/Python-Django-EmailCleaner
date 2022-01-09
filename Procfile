web: gunicorn --chdir /app/gmailautocleaner gmailautocleaner.wsgi
celery: celery -A gmailautocleaner --workdir gmailautocleaner worker -l info