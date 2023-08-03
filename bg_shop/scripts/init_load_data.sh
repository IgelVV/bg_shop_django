#!/bin/bash

# Colors
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Working directory # todo (-add args)
#cd /app || exit 1

# Migration
echo -e "\n${PURPLE}Running migration...${NC}\n"

python manage.py migrate

# Creating superuser (better do this in a migration)
echo -e "\n${PURPLE}Creating superuser...${NC}\n"

export DJANGO_SUPERUSER_PASSWORD=password
export DJANGO_SUPERUSER_EMAIL=admin@mail.com
export DJANGO_SUPERUSER_USERNAME=admin

python manage.py createsuperuser --no-input

# Loading data from fixtures
echo -e "\n${PURPLE}Loading data from fixtures...${NC}\n"
# common
python manage.py loaddata initial_image.json
echo -e "${PURPLE}initial_image.json is loaded.${NC}\n"
# profile
python manage.py loaddata initial_profile.json
echo -e "${PURPLE}initial_profile.json is loaded.${NC}\n"
# shop
python manage.py loaddata initial_category.json
echo -e "${PURPLE}initial_category.json is loaded.${NC}\n"
python manage.py loaddata initial_specification.json
echo -e "${PURPLE}initial_specification.json is loaded.${NC}\n"
python manage.py loaddata initial_tag.json
echo -e "${PURPLE}initial_tag.json is loaded.${NC}\n"
python manage.py loaddata initial_product.json
echo -e "${PURPLE}initial_product.json is loaded.${NC}\n"
python manage.py loaddata initial_banner.json
echo -e "${PURPLE}initial_banner.json is loaded.${NC}\n"
python manage.py loaddata initial_sale.json
echo -e "${PURPLE}initial_sale.json is loaded.${NC}\n"
python manage.py loaddata initial_review.json
echo -e "${PURPLE}initial_review.json is loaded.${NC}\n"
#orders
python manage.py loaddata initial_order.json
echo -e "${PURPLE}initial_order.json is loaded.${NC}\n"
python manage.py loaddata initial_ordered_product.json
echo -e "${PURPLE}initial_ordered_product.json is loaded.${NC}\n"

echo "-------------------------------"
echo -e "${GREEN}Initial setup is complete.${NC}"
echo -e "-------------------------------\n"