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


if __name__ == '__main__':
    conn = create_connection("positions.db")
    curs = conn.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS position (
        id INTEGER PRIMARY KEY,
        name text NOT NULL,
        positionX REAL NOT NULL,
        positionY REAL NOT NULL,
        positionZ REAL NOT NULL,
        rotation REAL NOT NULL
    );
    '''
    curs.execute(sql)
    conn.close()
