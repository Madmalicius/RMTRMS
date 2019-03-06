import sqlite3
from sqlite3 import Error
import triad_openvr
import time

v = triad_openvr.triad_openvr()
v.print_discovered_objects()


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def update_position(curs, params):

    sql = '''
UPDATE OR IGNORE position SET positionX=:positionX, 
                    positionY=:positionY, 
                    positionZ=:positionZ,
                    yaw=:yaw
WHERE name = :name;
'''

    try:
        curs.execute(sql, params)
    except Error as e:
        print(e)

    sql = '''
INSERT or IGNORE INTO position (name, 
                                positionX, 
                                positionY, 
                                positionZ, 
                                yaw)
VALUES(:name, :positionX, :positionY, :positionZ, :yaw);
    '''
    try:
        curs.execute(sql, params)
    except Error as e:
        print(e)

    return curs.lastrowid


if __name__ == '__main__':

    conn = create_connection("positions.db")
    curs = conn.cursor()
    for i in range(0, 10):
        pose = v.devices["tracker_1"].get_pose_euler()
        x = pose[0]
        y = pose[1]
        z = pose[2]
        yaw = pose[4]
        print(pose)
        params = {"id": 1,
                  "name": "Machine 1",
                  "positionX": x,
                  "positionY": y,
                  "positionZ": z,
                  "yaw": yaw}
        update_position(curs, params)
        conn.commit()
        time.sleep(1)
    conn.close()
