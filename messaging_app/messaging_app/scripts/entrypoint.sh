#!/usr/bin/env bash
set -e

# Optional database readiness wait (uncomment if needed)
# until python - <<'PY'
# import os, sys, time, socket
# host=os.environ.get('DB_HOST','127.0.0.1'); port=int(os.environ.get('DB_PORT','3306'))
# s=socket.socket(); 
# err=s.connect_ex((host,port)); 
# sys.exit(0 if err==0 else 1)
# PY
# do echo "Waiting for DB..."; sleep 2; done

python manage.py collectstatic --noinput || true
python manage.py migrate --noinput || true
exec gunicorn messaging_app.wsgi:application --bind 0.0.0.0:8000 --workers 3
