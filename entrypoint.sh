#!/bin/bash

python manage.py migrate
python manage.py populate_db --type all

# Executa o comando passado para o container
exec "$@"