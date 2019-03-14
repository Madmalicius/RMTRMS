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

    sql = """
UPDATE OR IGNORE position SET positionX=:positionX, 
                    positionY=:positionY, 
                    positionZ=:positionZ,
                    yaw=:yaw,
                    pitch=:pitch,
                    roll=:roll
WHERE serial = :serial;
"""

    try:
        curs.execute(sql, params)
    except Error as e:
        print(e)

    sql = """
INSERT or IGNORE INTO position (name,
                                serial,
                                positionX, 
                                positionY, 
                                positionZ, 
                                yaw,
                                pitch,
                                roll)
VALUES(:name, :serial, :positionX, :positionY, :positionZ, :yaw, :pitch, :roll);
    """
    try:
        curs.execute(sql, params)
    except Error as e:
        print(e)

    return curs.lastrowid


if __name__ == "__main__":

    conn = create_connection("positions.db")
    curs = conn.cursor()
    curs.execute("PRAGMA main.synchronous=NORMAL")
    serial = v.devices["tracker_1"].get_serial()
    print(serial)
    for i in range(0, 1000000):
        pose = v.devices["tracker_1"].get_pose_euler()
        x = pose[0]
        z = pose[1]
        y = pose[2]
        yaw = pose[3]
        pitch = pose[4]
        roll = pose[5]
        print(pose)
        params = {
            "name": "Machine 1",
            "serial": serial,
            "positionX": x,
            "positionY": y,
            "positionZ": z,
            "yaw": yaw,
            "pitch": pitch,
            "roll": roll,
        }
        update_position(curs, params)
        conn.commit()
        time.sleep(0.01)
    conn.close()
