CREATE DATABASE users;
USE users;

CREATE TABLE guest (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    kanji_name VARCHAR(30),
    kana_name VARCHAR(30),
    relation LONGTEXT,
    reward BIT(1) NOT NULL,
    attendance BIT(1) NOT NULL,
    uuid VARCHAR(32) NOT NULL
    note LONGTEXT,
);

CREATE TABLE IF NOT EXISTS host (
    account,
    password,
    salt
);
