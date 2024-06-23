#!/bin/sh

cd "$(dirname "$0")"

if [ -f ".env" ]; then
    source .env
fi

{% if "django" in cookiecutter.extra_packages -%}

if [ "$DATABASE_URL" = "" ]; then
    echo DATABASE_URL not set, aborting.
    exit 1
fi

python manage.py migrate --check
if [ $? -ne 0 ]; then
    echo running migrations before starting app
    python manage.py migrate
fi

gunicorn -w ${WORKERS:-1} core_sim.wsgi --access-logfile - --bind 0.0.0.0:8000

{% elif "sqlalchemy" in cookiecutter.extra_packages -%}
if [ "$SQLALCHEMY_DATABASE_URI" = "" ]; then
    echo SQLALCHEMY_DATABASE_URI not set, aborting.
    exit 1
fi

# Check for pending migrations
current_migration=$(alembic current | awk '{print $1}')
latest_migration=$(alembic heads | awk '{print $1}')

if [ "$current_migration" != "$latest_migration" ]; then
    echo "Running migrations before starting app"
    alembic upgrade head
fi

uvicorn main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-1}

{% else -%}
/bin/sleep 100000
{% endif -%}
