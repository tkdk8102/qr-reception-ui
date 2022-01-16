CREATE DATABASE users;
USE users;

CREATE TABLE guests (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    gid VARCHAR(32) NOT NULL,
    attendance TINYINT(1),
    kanji_name VARCHAR(30),
    kana_name VARCHAR(30),
    relation LONGTEXT,
    reward LONGTEXT,
    note LONGTEXT
);

CREATE TABLE hosts (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    account VARCHAR(30) UNIQUE,
    password VARCHAR(60)
);
