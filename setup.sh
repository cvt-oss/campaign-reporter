#!/bin/sh
echo "Waiting for postgres"
sleep 3 # for postgres
echo "Loading new migrations"
./manage.py migrate
echo "Starting web server"
./manage.py runserver 0.0.0.0:8000
