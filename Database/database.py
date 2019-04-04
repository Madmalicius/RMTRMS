import sqlite3
from sqlite3 import Error as sqliteError


class database:
    def __init__(self, db):
        try:
            self.db = sqlite3.connect(db)
        except sqliteError as e:
            print(e)
        self.curs = self.db.cursor()

    def assign_tracker(self, module, tracker):
        """ assign a tracker serial to a module """

        params = {"module": module, "tracker": tracker}

        sql = """
            UPDATE modules SET tracker=:tracker WHERE module=:module
              """

        try:
            self.curs.execute(sql, params)
        except sqliteError as e:
            print(e)

    def update_positionIn(self, tracker):
        """ update the position of a tracker in the database """

        params = {
            "serial": tracker.serial,
            "positionX": tracker.x,
            "positionY": tracker.y,
            "positionZ": tracker.z,
            "yaw": tracker.yaw,
            "pitch": tracker.pitch,
            "roll": tracker.roll,
        }

        sql = """
                UPDATE positionIn SET positionX=:positionX, 
                                    positionY=:positionY, 
                                    positionZ=:positionZ,
                                    yaw=:yaw,
                                    pitch=:pitch,
                                    roll=:roll
                WHERE serial = :serial;
                """

        try:
            self.curs.execute(sql, params)
        except sqliteError as e:
            print(e)

        try:
            self.curs.execute("SELECT changes()")
            if self.curs.fetchone()[0] is 0:
                sql = """
                INSERT or IGNORE INTO positionIn (serial,
                                        positionX,
                                        positionY,
                                        positionZ,
                                        yaw,
                                        pitch,
                                        roll)
                VALUES(:serial, :positionX, :positionY, :positionZ, :yaw, :pitch, :roll);
                """
                try:
                    self.curs.execute(sql, params)
                except sqliteError as e:
                    print(e)

                # update name based on ID if no name is given
                params2 = {
                    "name": "Tracker " + str(self.curs.lastrowid),
                    "serial": params["serial"],
                }

                sql = """
                UPDATE or IGNORE positionIn SET name=:name WHERE serial = :serial AND name IS NULL;
                """

                self.curs.execute(sql, params2)
        except sqliteError as e:
            print(e)

        self.db.commit()

    def check_close(self):
        return self.curs.execute("SELECT close FROM terminate").fetchone()[0]
