import sqlite3
from sqlite3 import Error as sqliteError


class Tracker:
    def __init__(self, vr=None, db=None, trackerID=None, serial=None):
        self.db = db
        if vr:
            self.vr = vr
            self.trackerID = trackerID
            self.serial = self.vr.devices[self.trackerID].get_serial()
            self.name = db.get_tracker_name(self)

            if self.name == None:
                self.db.set_default_tracker_name(self)
                self.name = self.db.get_tracker_name(self)

            self.active = True
            self.update_position()
            self.db.set_tracker_active_status(self, True)
        else:
            self.serial = serial
            self.name = self.db.get_tracker_name(self)
            self.active = False
            self.db.set_tracker_active_status(self, False)

    def update_position(self):
        if self.active is True:
            try:
                pose = self.vr.devices[self.trackerID].get_pose_euler()
            except AttributeError:
                self.active = False
                return None
            except KeyError:
                self.active = False
                return None

            if pose == [0, 0, 0, 0, 0, 0]:
                self.active = False
                return None

            self.x = pose[0]
            self.z = pose[1]
            self.y = pose[2]
            self.pitch = pose[3]
            self.yaw = pose[4]
            self.roll = pose[5]

            self.db.update_tracker_position(self)
        else:
            try:
                pose = self.vr.devices[self.trackerID].get_pose_euler()
                self.active = True
            except AttributeError:
                pass
            except KeyError:
                pass

    def rename(self, name):
        self.db.set_tracker_name(self, name)
        self.name = name


class Database:
    def __init__(self, db, vr=None):
        self.databasePath = db
        try:
            self.db = sqlite3.connect(db)
        except sqliteError as e:
            print(e)
        self.curs = self.db.cursor()
        self.curs.execute("PRAGMA main.synchronous=NORMAL")

        if vr is not None:
            self.vr = vr

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
        """Returns a list of tracker objects.
        
        Returns:
            List -- list of Tracker objects
        """

        try:
            trackerList = self.curs.execute("SELECT serial FROM trackers").fetchall()
            for index, tracker in enumerate(trackerList):
                trackerList[index] = tracker[0]

            activeTrackers = []

            self.vr.update_device_list()
            for device in self.vr.devices:
                if "tracker" not in device:
                    continue

                activeTrackers.append(Tracker(vr=self.vr, db=self, trackerID=device))

            for tracker in activeTrackers:
                try:
                    trackerList.remove(tracker.serial)
                except ValueError:
                    pass

            for index, tracker in enumerate(trackerList):
                trackerList[index] = Tracker(db=self, serial=tracker)

            trackerList.extend(activeTrackers)

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
        except TypeError:
            return None

    def get_assigned_tracker(self, module):
        """Returns the tracker assigned to a module. 


        Arguments:
            module {String} -- The module whose tracker will be returned.
        
        Returns:
            tracker {Tracker} -- Tracker that is assigned to the module.
        """

        try:
            tracker = self.curs.execute(
                "SELECT tracker FROM modules WHERE module=:module", {"module": module}
            ).fetchone()[0]

            if tracker:
                trackerList = self.get_tracker_list()
                for trackerFromList in trackerList:
                    if tracker == trackerFromList.serial:
                        tracker = trackerFromList
                        break
                return tracker
            else:
                return None

        except sqliteError as e:
            print(e)
            return None

    def set_module_tracking_status(self, module, status):
        """Sets the tracking status of the specified module.
        
        Arguments:
            module {String} -- The module of which the status will be modified.
            status {bool} -- The tracking status of the module. 1 for tracking, 0 for not tracking.
        """

        try:
            self.curs.execute(
                "UPDATE modules SET tracked=:status WHERE module=:module",
                (status, module),
            )
        except sqliteError as e:
            print(e)

        self.db.commit()

    def set_tracker_active_status(self, tracker, status):
        """Sets the active status of the specified tracker in the database

        Arguments:
            tracker {Tracker} -- The active of which the status will be modified.
            status {bool} -- The active status of the tracker.
        """
        try:
            self.curs.execute(
                "UPDATE trackers SET active=:status WHERE serial=:serial",
                (status, tracker.serial),
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

    def set_default_tracker_name(self, tracker):
        try:
            self.curs.execute(
                "SELECT serial FROM trackers WHERE serial=:serial;",
                {"serial": tracker.serial},
            )

            params = {
                "name": "Tracker " + str(self.curs.lastrowid),
                "serial": tracker.serial,
            }

            self.curs.execute(
                "UPDATE trackers SET name=:name WHERE serial=:serial AND name IS NULL;",
                params,
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
            self.curs.execute(
                "UPDATE modules SET tracker=NULL, tracked=0 WHERE tracker=:tracker",
                {"tracker": tracker.serial},
            )
            self.curs.execute(sql, params)
        except sqliteError as e:
            print(e)

        self.db.commit()

    def update_tracker_position(self, tracker):
        """Updates the position of the tracker in the database
        
        Arguments:
            tracker {Tracker} -- The tracker whose position will be updated in the database
        """

        if tracker.active == False:
            print("Error: Tracker is not tracked\n")
            return None

        params = {
            "serial": tracker.serial,
            "active": tracker.active,
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
                INSERT INTO trackers (serial,
                                        active,
                                        positionX,
                                        positionY,
                                        positionZ,
                                        yaw,
                                        pitch,
                                        roll)
                VALUES(:serial, :active, :positionX, :positionY, :positionZ, :yaw, :pitch, :roll);
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
                UPDATE trackers SET name=:name WHERE serial = :serial AND name IS NULL;
                """

                self.curs.execute(sql, params2)
        except sqliteError as e:
            print(e)

        self.db.commit()

    def remove_tracker(self, tracker):
        """Removes the specified tracker from the database

        parameters:
            tracker {Tracker} -- The tracker will be deleted
        """

        try:
            self.curs.execute(
                "DELETE FROM trackers WHERE serial = :serial",
                {"serial": tracker.serial},
            )
            self.db.commit()
        except sqliteError as e:
            print(e)

    def check_close(self):
        """Checks the close field of the database

        Returns:
            int -- 1 if the program should close
        """

        return self.curs.execute("SELECT close FROM terminate").fetchone()[0]
