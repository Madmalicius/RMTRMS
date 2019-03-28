import sqlite3
from sqlite3 import Error
import triad_openvr
import time
import tkinter as tk
from tkinter import filedialog

root = tk.Tk("Select Database file")
root.withdraw()


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
UPDATE or IGNORE positionIn SET positionX=:positionX, 
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
INSERT or IGNORE INTO positionIn (name,
                                serial,
                                positionX, 
                                positionY, 
                                positionZ, 
                                yaw,
                                pitch,
                                roll)
VALUES("MachineName", :serial, :positionX, :positionY, :positionZ, :yaw, :pitch, :roll);
    """
    try:
        curs.execute(sql, params)
    except Error as e:
        print(e)

    return curs.lastrowid


def exit_program(conn=None):
    if conn is not None:
        conn.close()
    exit()


if __name__ == "__main__":

    vr = triad_openvr.triad_openvr()
    vr.print_discovered_objects()

    databasePath = filedialog.askopenfilename()
    if databasePath is "":
        exit_program()

    conn = create_connection(databasePath)
    curs = conn.cursor()
    curs.execute("PRAGMA main.synchronous=NORMAL")

    try:
        curs.execute("UPDATE terminate SET close=0 WHERE id=1")
        conn.commit()
    except Error as e:
        print(e)

    trackerCount = 0
    while trackerCount is 0:
        print("\rSearching for trackers", end="")
        vr.update_device_list()
        for device in vr.devices:
            if "tracker" not in device:
                continue
            else:
                trackerCount += 1
    print("\nTrackers found!\n\n")

    while True:
        for device in vr.devices:
            if "tracker" not in device:
                continue
            serial = vr.devices[device].get_serial()
            pose = vr.devices[device].get_pose_euler()
            x = pose[0]
            z = pose[1]
            y = pose[2]
            yaw = pose[3]
            pitch = pose[4]
            roll = pose[5]
            params = {
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
            print("updated " + serial)
            time.sleep(0.01)

        if curs.execute("SELECT close FROM terminate").fetchone()[0]:
            exit_program(conn)
