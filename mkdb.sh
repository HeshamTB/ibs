#!/bin/bash

# Make a new database
# Mar 3, 2022 - H.B. 

if [ -z ${1} ]
then
    echo "Enter a databse name to use this"
    exit 1
fi

sqlite3 ${1} << EOF
CREATE TABLE user_accounts(
    id           INTEGER(512) PRIMARY KEY NOT NULL,
    username     TEXT(64)                 NOT NULL,
    date_created datetime                         ,
    digest       TEXT                     NOT NULL,
    salt         TEXT
);
CREATE TABLE iot_entity(
    id          INTEGER(512) PRIMARY KEY NOT NULL,
    description TEXT,
    last_connection datetime,
);
EOF

