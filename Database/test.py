from database import Database
from trackers import Tracker
import triad_openvr
import configparser
import time
import threading
from threading import Thread, Lock

databaseLock = Lock()


def search_for_tracker(vr):
    trackerCount, searchCount = 0, 0
    while trackerCount is 0 and searchCount < 5000:
        print("\rSearching for trackers", end="")
        vr.update_device_list()
        for device in vr.devices:
            if "tracker" not in device:
                searchCount += 1
                time.sleep(0.001)
                continue
            else:
                trackerCount += 1
    print("\n\n Number of trackers: ")
    print(trackerCount)
    time.sleep(0.5)


def update_trackers(database, trackers):
    database = Database(database.databasePath)
    global databaseLock

    time.sleep(2)
    while True:
        if threading.main_thread().isAlive():
            pass
        else:
            exit()

        databaseLock.acquire()

        for tracker in trackers:
            tracker.update_position()
            database.update_tracker_position(tracker)
            print("updated " + tracker.serial)

        databaseLock.release()
        time.sleep(1)


def test_tracking_status(database):
    database = Database(database.databasePath)
    global databaseLock

    time.sleep(2)
    while True:
        if threading.main_thread().isAlive():
            pass
        else:
            exit()

        databaseLock.acquire()

        database.set_tracking_status("CNC", 1)
        print(database.get_tracking_status("CNC"))
        time.sleep(1)

        database.set_tracking_status("CNC", 0)
        print(database.get_tracking_status("CNC"))

        databaseLock.release()
        time.sleep(1)


def test_name(database, tracker):
    database = Database(database.databasePath)
    global databaseLock

    time.sleep(2)
    while True:
        if threading.main_thread().isAlive():
            pass
        else:
            exit()

        databaseLock.acquire()

        database.set_tracker_name(tracker, "Robit")
        print(database.get_tracker_name(tracker))
        time.sleep(1)
        database.set_tracker_name(tracker, "John")
        print(database.get_tracker_name(tracker))

        databaseLock.release()
        time.sleep(1)


def test_assign_tracker(database):
    pass


if __name__ == "__main__":
    vr = triad_openvr.triad_openvr()

    search_for_tracker(vr)

    vr.print_discovered_objects()

    config = configparser.ConfigParser()
    config.read("config")
    databasePath = config.get("database", "path")

    database = Database(databasePath)

    trackers = []

    for device in vr.devices:
        if "tracker" not in device:
            continue
        newTracker = Tracker(vr, device)
        trackers.append(newTracker)

    print("\n\n")

    update_trackers_thread = Thread(
        target=update_trackers, args=[database, trackers], daemon=False
    )

    test_assign_tracker_thread = Thread(
        target=test_assign_tracker, args=[database], daemon=False
    )

    test_name_thread = Thread(
        target=test_name, args=[database, trackers[0]], daemon=False
    )

    update_trackers_thread.start()
    test_assign_tracker_thread.start()
    test_name_thread.start()

    moduleList = database.get_module_list()

    for module in moduleList:
        print(module)

    trackerList = database.get_tracker_list()

    for tracker in trackerList:
        print(tracker)

    while True:
        input()
        exit()
