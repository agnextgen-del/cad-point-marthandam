#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/skillpro_django"
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
python manage.py migrate
python manage.py ensure_admin
echo
echo "==================================================="
echo " Website  : http://127.0.0.1:8000/"
echo " Dashboard: http://127.0.0.1:8000/students-details/skillpro-dashboard.html"
echo "==================================================="
python manage.py runserver 8000
