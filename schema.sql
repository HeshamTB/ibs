CREATE TABLE user_accounts(
    user_id UNSIGHNED INT PRIMARY KEY NOT NULL,
    username NCHAR(64) NOT NULL,
    email    NCHAR(64) NOT NULL,
    date_created DATETIME,
    digest   NCHAR(512) NOT NULL,
    salt NCHAR(64) NOT NULL
);
