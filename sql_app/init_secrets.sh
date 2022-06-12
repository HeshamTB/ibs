#!/bin/bash

echo "API_KEY=$(./gen_secret.sh)" >> .env
echo "API_KEY_NAME=big_boy" >> .env
echo "jwt_secret=$(./gen_secret.sh)" >> .env
echo "jwt_algorithm=HS256" >> .env

read -s -p "First User password: " firstpass
echo 
read -s -p "Retype First User password: " secondpass
echo

if [ $firstpass != $secondpass ];
then
    echo "Passwords dont match!"
    exit 255
fi
echo "first_user_pass=$firstpass" >> .env

chmod 600 .env
