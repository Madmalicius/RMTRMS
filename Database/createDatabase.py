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


if __name__ == "__main__":
    conn = create_connection("Modules.db")
    curs = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS positionIn (
    id INTEGER PRIMARY KEY,
    name text NOT NULL,
    serial text UNIQUE NOT NULL,
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
    name text NOT NULL,
    serial text UNIQUE NOT NULL,
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
