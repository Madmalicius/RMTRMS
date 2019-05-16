#!/usr/bin/env python
""" Creates a database for the RMTRMS project in the current directory"""

import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def create_database(path="Modules.db"):
    conn = create_connection(path)
    curs = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS trackers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    serial TEXT UNIQUE NOT NULL,
    active BOOL NOT NULL,
    positionX FLOAT NOT NULL,
    positionY FLOAT NOT NULL,
    positionZ FLOAT NOT NULL,
    yaw FLOAT NOT NULL,
    pitch FLOAT NOT NULL,
    roll FLOAT NOT NULL
    );
    """
    try:
        curs.execute(sql)
    except Error as e:
        print(e)

    sql = """
    PRAGMA journal_mode=WAL;
    """
    try:
        curs.execute(sql)
    except Error as e:
        print(e)

    sql = """
    CREATE TABLE IF NOT EXISTS positionOut (
    id INTEGER PRIMARY KEY,
    module TEXT UNIQUE NOT NULL,
    positionX FLOAT NOT NULL,
    positionY FLOAT NOT NULL,
    yaw FLOAT NOT NULL
    );
    """
    try:
        curs.execute(sql)
    except Error as e:
        print(e)

    sql = """
    CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY,
    module TEXT UNIQUE NOT NULL,
    tracker TEXT UNIQUE,
    tracked BIT NOT NULL
    );
    """
    try:
        curs.execute(sql)
    except Error as e:
        print(e)

    sql = """
    CREATE TABLE IF NOT EXISTS terminate (
    id INTEGER PRIMARY KEY,
    close BIT NOT NULL
    );
    """
    try:
        curs.execute(sql)
    except Error as e:
        print(e)

    try:
        curs.execute("INSERT INTO terminate (close) VALUES (0)")
    except Error as e:
        print(e)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
