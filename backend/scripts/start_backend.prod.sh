while ! nc -q 1 $POSTGRES_HOST $POSTGRES_PORT </dev/null; do sleep 5; done

python3 manage.py migrate && \
python3 manage.py initadmin && \
python3 manage.py setup_tasks && \
python3 manage.py collectstatic --no-input && \
gunicorn lotus.wsgi:application -w 4 --threads 4 -b :8000 --reload
