import sqlite3
from sqlite3 import Error as sqliteError


class Tracker:
    def __init__(self, vr, trackerID):
        self.vr = vr
        self.trackerID = trackerID
        self.serial = self.vr.devices[self.trackerID].get_serial()
        self.name = ""
        pose = self.vr.devices[self.trackerID].get_pose_euler()
        self.x = pose[0]
        self.z = pose[1]
        self.y = pose[2]
        self.yaw = pose[3]
        self.pitch = pose[4]
        self.roll = pose[5]

    def update_position(self):
        pose = self.vr.devices[self.trackerID].get_pose_euler()
        self.x = pose[0]
        self.z = pose[1]
        self.y = pose[2]
        self.yaw = pose[3]
        self.pitch = pose[4]
        self.roll = pose[5]


class Database:
    def __init__(self, db):
        self.databasePath = db
        try:
            self.db = sqlite3.connect(db)
        except sqliteError as e:
            print(e)
        self.curs = self.db.cursor()

    def get_module_list(self):
        """Returns a list of modules.

        Returns:
            List -- list of Strings with module names.
        """

        try:
            moduleList = self.curs.execute("SELECT module FROM modules").fetchall()
            for index, module in enumerate(moduleList):
                moduleList[index] = module[0]
            return moduleList
        except sqliteError as e:
            print(e)
            return None

    def get_tracker_list(self):
        """Returns a list of tracker serials.
        
        Returns:
            List -- list of Strings with known tracker serials.
        """

        try:
            trackerList = self.curs.execute("SELECT serial FROM trackers").fetchall()
            for index, tracker in enumerate(trackerList):
                trackerList[index] = tracker[0]
            return trackerList
        except sqliteError as e:
            print(e)
            return None

    def get_tracking_status(self, module):
        """Returns the tracking status of the specified module.
        
        Arguments:
            module {String} -- The module of which the tracking status will be returned.
        
        Returns:
            bool -- Tracking status of the module.
        """

        try:
            tracked = self.curs.execute(
                "SELECT tracked FROM modules WHERE module=:module", (module,)
            ).fetchone()[0]
            return tracked
        except sqliteError as e:
            print(e)
            return None

    def get_tracker_name(self, tracker):
        """Returns the name of the tracker.
        
        Arguments:
            tracker {Tracker} -- The tracker of which the name will be returned.
        
        Returns:
            String -- Name of specified module.
        """

        try:
            return self.curs.execute(
                "SELECT name FROM trackers WHERE serial=:serial", (tracker.serial,)
            ).fetchone()[0]
        except sqliteError as e:
            print(e)

    def set_tracking_status(self, module, status):
        """Sets the tracking status of the specified module.
        
        Arguments:
            module {String} -- The module of which the status will be modified.
            status {int} -- The tracking status of the module. 1 for tracking, 0 for not tracking.
        """

        try:
            self.curs.execute(
                "UPDATE modules SET tracked=:status WHERE module=:module",
                (status, module),
            )
        except sqliteError as e:
            print(e)

        self.db.commit()

    def set_tracker_name(self, tracker, name):
        """Sets the name of the tracker.

        Arguments:
            tracker {Tracker} -- The tracker of which the name will be modified.
            name {String} -- The name which will be assigned to the tracker.
        """

        try:
            self.curs.execute(
                "UPDATE trackers SET name=:name WHERE serial=:serial",
                (name, tracker.serial),
            )
        except sqliteError as e:
            print(e)

        self.db.commit()

    def assign_tracker(self, module, tracker):
        """Assigns a tracker serial to a module.
        
        Arguments:
            module {String} -- The module to which the tracker will be assigned.
            tracker {Tracker} -- The tracker which will be assigned to the module
        """

        params = {"module": module, "tracker": tracker.serial}

        sql = """
            UPDATE modules SET tracker=:tracker WHERE module=:module
              """

        try:
            self.curs.execute(sql, params)
        except sqliteError as e:
            print(e)

        self.db.commit()

    def update_tracker_position(self, tracker):
        """Updates the position of the tracker in the database
        
        Arguments:
            tracker {Tracker} -- The tracker whose position will be updated in the database
        """

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
                UPDATE trackers SET positionX=:positionX, 
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
                INSERT or IGNORE INTO trackers (serial,
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
                UPDATE or IGNORE trackers SET name=:name WHERE serial = :serial AND name IS NULL;
                """

                self.curs.execute(sql, params2)
        except sqliteError as e:
            print(e)

        self.db.commit()

    def check_close(self):
        """Checks the close field of the database

        Returns:
            int -- 1 if the program should close
        """

        return self.curs.execute("SELECT close FROM terminate").fetchone()[0]
