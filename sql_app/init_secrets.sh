#!/bin/bash

echo "API_KEY=$(./gen_secret.sh)" >> .env
echo "API_KEY_NAME=big_boy" >> .env
echo "jwt_secret=$(./gen_secret.sh)" >> .env
echo "jwt_algorithm=HS256" >> .env
