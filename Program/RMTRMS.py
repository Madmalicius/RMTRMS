import sqlite3
from sqlite3 import Error as sqliteError
import bottle
import triad_openvr
from openvr import OpenVRError


class SteamVRNotFoundError(Exception):
    """ Raised when SteamVR is not installed"""

    pass


class Tracker:
    def __init__(self, vr=None, db=None, trackerID=None, serial=None):
        self.db = db
        if vr:
            self.vr = vr
            self.trackerID = trackerID
            self.index = self.vr.devices[self.trackerID].index
            self.serial = self.vr.devices[self.trackerID].get_serial()
            self.db.set_tracker_active_status(self, True)
            self.update_position()
            self.name = db.get_tracker_name(self)

            if self.name == None:
                self.db.set_default_tracker_name(self)
                self.name = self.db.get_tracker_name(self)

        else:
            self.serial = serial
            self.name = self.db.get_tracker_name(self)
            self.db.set_tracker_active_status(self, False)

    def update_position(self):
        """Updates the position of the tracker if it is active.
        """
        if self.active is True:
            try:
                pose = self.vr.devices[self.trackerID].get_pose_euler()
            except AttributeError:
                self.db.set_tracker_active_status(self, False)
                return None
            except KeyError:
                self.db.set_tracker_active_status(self, False)
                return None

            if pose == [0, 0, 0, 0, 0, 0]:
                self.db.set_tracker_active_status(self, False)
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
                self.db.set_tracker_active_status(self, True)
            except AttributeError:
                pass
            except KeyError:
                pass

    def rename(self, name):
        """Renames the tracker in the database
        
        Arguments:
            name {String} -- The new name for the tracker
        """

        self.db.set_tracker_name(self, name)
        self.name = name

    def identify(self):
        """Turns on the rumble output of the tracker for 1 second
        """
        self.db.vr.vr.triggerHapticPulse(self.index, 0, 1000000)


class Database:
    """Database object that can interact with an SQlite database, as well as OpenVR.

    Arguments:
        db {String} -- Path to database
    """

    def __init__(self, db, vr=True):
        self.databasePath = db
        try:
            self.db = sqlite3.connect(db)
        except sqliteError as e:
            print(e)
        self.curs = self.db.cursor()
        self.curs.execute("PRAGMA main.synchronous=NORMAL")

        if vr:
            try:
                self.vr = triad_openvr.triad_openvr()
            except OpenVRError:
                raise SteamVRNotFoundError

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

            trackerList = self.get_tracker_list()
            for trackerFromList in trackerList:
                if tracker == trackerFromList.serial:
                    tracker = trackerFromList
                    break
            return tracker

        except sqliteError as e:
            print(e)
            return None
        except TypeError:
            return None

    def get_assigned_module(self, tracker):
        """Returns the module which the tracker is assigned to
        
        Arguments:
            tracker {Tracker} -- Tracker whose assigned module will be returned

        Returns:
            module {String} -- Name of the module which the tracker is assigned to
        """

        try:
            module = self.curs.execute(
                "SELECT module FROM modules WHERE tracker=:serial",
                {"serial": tracker.serial},
            ).fetchone()[0]

            return module
        except sqliteError as e:
            print(e)
            return None
        except TypeError:
            return None

    def get_module_position(self, module):
        """Returns the position of the specified module
        
        Arguments:
            module {String} -- The name of the module
        """

        try:
            position = self.curs.execute("SELECT positionX,positionY,yaw FROM positionOut WHERE module=:module", {"module" : module}).fetchone()
            return position
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
            tracker.active = status
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
            tracker.name = name
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
            self.curs.execute(
                "UPDATE modules SET tracker=NULL, tracked=0 WHERE tracker=:serial",
                {"serial": tracker.serial},
            )
            self.db.commit()
        except sqliteError as e:
            print(e)

class Server:
    """Server object that returns 7 values

    The output is in the format:
    {Bool} {Float} {Float} {Float} {Float} {Float} {Float}

    These correspond to:
    Tracker Active -- Tracker X Position -- Tracker Y Position -- Tracker Yaw -- Module X Position -- Module Y Position -- Module Yaw
    """
    def __init__(self, databasePath=None, host="0.0.0.0", port=8000):
        self._database = Database(databasePath)

        self._host = host
        self._port = port
        self._app = bottle.Bottle()
        self._route()

    def _route(self):
        self._app.route("/modules/<module_name>", callback=self.get_module)

    def start(self):
        """Run the server
        """
        self._app.run(host=self._host, port=self._port, debug=False)

    def stop(self):
        """Stop the server
        """
        self._app.close()

    def get_module(self, module_name=None):
        """Return the desired module's tracker and position information
        
        Keyword Arguments:
            module_name {String} -- Name of the module as it appears in the database (case sensitive) (default: {None})
        
        Returns:
            Active {Bool} -- The active status of the assigned tracker.
            Tracker Position X {Float} -- X position of the assigned tracker.
            Tracker Position Y {Float} -- Y position of the assigned tracker.
            Tracker Yaw {Float} -- Yaw of the assigned tracker.
            Module Position X {Float} -- Desired X position of the specified module
            Module Position Y {Float} -- Desired Y position of the specified module
            Module Yaw {Float} -- Desired yaw of the specified module
        """
        tracker = self._database.get_assigned_tracker(module_name)
        
        if tracker is None:
            return "0 0 0 0 0 0 0"

        moduleX, moduleY, moduleYaw = self._database.get_module_position(module_name)

        if tracker.active:
            response = "{:b} {:f} {:f} {:f} {:f} {:f} {:f}".format(
                1, tracker.x, tracker.y, tracker.yaw, moduleX, moduleY, moduleYaw
            )
        else:
            response = "0 0 0 0 0 0 0"

        return response