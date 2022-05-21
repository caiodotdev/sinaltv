web: gunicorn sinaltv.wsgi --log-file -

worker: celery -A app beat -l info & celery -A app worker -l INFO -c 1 & wait -n

