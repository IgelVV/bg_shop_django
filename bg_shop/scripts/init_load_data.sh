#!/bin/bash

# work dir
cd /app || exit 1

# Migration
echo -e "\nRunning migration...\n"

python manage.py migrate

# Creating superuser (better do this in a migration)
echo -e "\nCreating superuser...\n"

export DJANGO_SUPERUSER_PASSWORD=password
export DJANGO_SUPERUSER_EMAIL=admin@mail.com
export DJANGO_SUPERUSER_USERNAME=admin

python manage.py createsuperuser --no-input

# Loading data from fixtures
echo -e "\nLoading data from fixtures...\n"

python manage.py loaddata initial_image.json
echo -e "initial_image.json is loaded.\n"
python manage.py loaddata initial_category.json
echo -e "initial_category.json is loaded.\n"
python manage.py loaddata initial_specification.json
echo -e "initial_specification.json is loaded.\n"
python manage.py loaddata initial_tag.json
echo -e "initial_tag.json is loaded.\n"
python manage.py loaddata initial_product.json
echo -e "initial_product.json is loaded.\n"
python manage.py loaddata initial_banner.json
echo -e "initial_banner.json is loaded.\n"
python manage.py loaddata initial_sale.json
echo -e "initial_sale.json is loaded.\n"
python manage.py loaddata initial_review.json
echo -e "initial_review.json is loaded.\n"

python manage.py loaddata initial_order.json
echo -e "initial_order.json is loaded.\n"
python manage.py loaddata initial_ordered_product.json
echo -e "initial_ordered_product.json is loaded.\n"

echo"-------------------------------"
echo -e "Initial setup is complete."
echo -e "-------------------------------\n"