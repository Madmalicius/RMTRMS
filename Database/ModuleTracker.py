#!/usr/bin/env python
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import threading
from threading import Thread
from time import sleep
import configparser
import triad_openvr
import createDatabase
from database import Database
from trackers import Tracker

root = tk.Tk()

root.title("Module Manager")
root.config(bg="#B0C4DE")

databasePathVar = tk.StringVar()
databasePath = ""

hltModule = StringVar()
hltTracker = StringVar()
trackers = StringVar()
trackerArr = []
checkButtonStatus = IntVar()


def search_for_tracker(vr):
    trackerCount, searchCount = 0, 0
    while trackerCount is 0 and searchCount < 5000:
        print("\rSearching for trackers", end="")
        vr.update_device_list()
        for device in vr.devices:
            if "tracker" not in device:
                searchCount += 1
                sleep(0.001)
                continue
            else:
                trackerCount += 1


def update_trackers(trackers, database):
    for tracker in trackers:
        tracker.update_position()
        database.update_tracker_position(tracker)
        print("updated " + tracker.serial)
    sleep(0.1)


def new_database():
    global databasePath, databasePathVar
    path = filedialog.asksaveasfilename(
        initialdir=".",
        title="Create new database",
        filetypes=[("db files", ".db"), ("all files", ".*")],
    )

    if path == "":
        return None

    if not path.endswith(".db"):
        path += ".db"

    createDatabase.create_database(path)
    databasePath = path
    databasePathVar.set("Database is: " + path)


def open_database():
    global databasePath, databasePathVar
    path = filedialog.askopenfilename(
        initialdir=".",
        title="Open database",
        filetypes=[("database files", ".db"), ("all files", ".*")],
    )

    if path == "":
        return None

    databasePath = path
    databasePathVar.set("Database is: " + path)


def manage_trackers():
    i = None

    # Create window
    trackerWindow = tk.Toplevel(root)
    trackerWindow.title("Manage Trackers")
    trackerWindow.grab_set()

    # Tracker list
    trackerList = tk.Listbox(trackerWindow)
    trackerList.grid(row=1, rowspan=5, padx=10, pady=10, sticky=E + W)

    for index, tracker in enumerate(trackerArr, start=0):
        if tracker == trackers.get():
            i = index
        trackerList.insert(index, tracker)

    # tracker renaming
    trackerNameLabel = tk.Label(trackerWindow, text="Rename tracker:")
    trackerNameLabel.grid(row=2, column=1, sticky=E + W)
    trackerName = tk.Entry(trackerWindow)
    trackerName.grid(row=2, column=2, sticky=E + W)

    acceptName = tk.Button(
        trackerWindow,
        text="Ok",
        command=lambda: update_tracker_list(trackerList, trackerName, trackerArr, i),
    )
    acceptName.grid(row=2, column=3)


def update_tracker_list(List, name, array, index):
    i = List.curselection()
    rename(List, name)

    print(i)
    trackerArr[i[0]] = name.get()
    trackers.set("")
    trackerDropdown["menu"].delete(0, "end")
    for tracker in trackerArr:
        trackerDropdown["menu"].add_command(
            label=tracker, command=tk._setit(trackers, tracker)
        )
    if index:
        trackers.set(trackerArr[index])
    else:
        trackers.set("Choose tracker")


def rename(List, name):
    i = List.curselection()
    print(i)
    if i:
        print("woo!")
        tmp = List.get(i[0])
        List.delete(i)
        List.insert(i, name.get())

    else:
        print("nooo!")


def updateModuleSelect(event, database):
    if moduleList.curselection():
        hltModule.set(moduleList.get(moduleList.curselection()))
        checkButtonStatus.set(database.get_tracking_status(hltModule.get()))
    else:
        hltModule.set("")


def trackerSelect(*args):
    # Check in DB where name is located
    hltTracker.set("this is " + trackers.get())
    print(trackers.get())


def toggleTracking(database):
    print("activated")
    print(checkButtonStatus.get())
    database.set_tracking_status(hltModule.get(), checkButtonStatus.get())


def testTread(trackers, databasePath):
    database = Database(databasePath)
    while threading.main_thread().isAlive():
        update_trackers(trackers, database)


if __name__ == "__main__":
    vr = triad_openvr.triad_openvr()
    vr.print_discovered_objects()

    config = configparser.ConfigParser()
    config.read("config")
    databasePath = config.get("database", "path")
    database = Database(databasePath)
    trackerList = []

    search_for_tracker(vr)
    for device in vr.devices:
        if "tracker" not in device:
            continue
        newTracker = Tracker(vr, device)
        trackerList.append(newTracker)

    menu = tk.Menu(root)

    # Create topmenu
    root.config(menu=menu)

    fileMenu = tk.Menu(menu, tearoff=False)
    trackerMenu = tk.Menu(menu, tearoff=False)

    # Add tabs to Menu
    menu.add_cascade(label="File", menu=fileMenu)
    menu.add_cascade(label="Trackers", menu=trackerMenu)

    # Add subtabs to File
    fileMenu.add_command(label="Create database", command=new_database)
    fileMenu.add_command(label="Open database", command=open_database)

    # Add subtabs to Trackers
    trackerMenu.add_command(label="Refresh")
    trackerMenu.add_command(label="Manage Trackers", command=manage_trackers)

    config = configparser.ConfigParser()
    try:
        config.read("config")
        databasePath = config.get("database", "path")
        databasePathVar.set("Database is: " + databasePath)
    except configparser.NoSectionError:
        open_database()
        config.add_section("database")
        config.set("database", "path", databasePath)

    with open("config", "w") as f:
        config.write(f)

    # Show path to active database
    databasePathWidget = tk.Label(root, textvariable=databasePathVar)
    databasePathWidget.grid(columnspan=5, sticky=E + W)

    # List of known modules
    moduleList = tk.Listbox(root)
    moduleList.bind(
        "<ButtonRelease-1>", lambda event: updateModuleSelect(event, database)
    )
    moduleList.grid(row=1, rowspan=5, padx=10, pady=10, sticky=N + S + W)
    modules = database.get_module_list()
    for index, module in enumerate(modules, start=0):
        moduleList.insert(index, module)

    # Highlighted module label
    moduleName = tk.Label(
        root, bg="white", relief=RIDGE, textvariable=hltModule, font=16
    )
    moduleName.grid(row=1, column=1, columnspan=2, sticky=E + W)

    # Tracker choice
    for i in range(0, 5):
        trackerArr.append("tracker " + str(i + 1))
    trackers.set("Choose tracker")
    trackers.trace("w", trackerSelect)
    trackerDropdown = tk.OptionMenu(root, trackers, *trackerArr)
    trackerDropdown.config(bg="white", fg="black")
    trackerDropdown["menu"].config(bg="white", fg="black")
    trackerDropdown.grid(row=2, column=1, sticky=N)

    # Tracker serial label
    hltTracker.set("No tracker chosen")
    trackerSerial = tk.Label(root, bg="white", relief=RIDGE, textvariable=hltTracker)
    trackerSerial.grid(row=2, column=2, sticky=E + W + N)

    # Checkbox for using tracker on module
    trackerCheckbox = tk.Checkbutton(
        root, text="Track module?", var=checkButtonStatus, command=lambda: toggleTracking(database)
    )
    trackerCheckbox.grid(row=3, column=1, sticky=N + E + W)

    # Create and run thread & GUI
    test = Thread(target=testTread, args=[trackerList, databasePath])
    test.start()

    root.mainloop()

