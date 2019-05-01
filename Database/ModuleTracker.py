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
from RMTRMS import Database, Tracker

root = tk.Tk()

root.title("Module Manager")
root.config(bg="#B0C4DE")

databasePathVar = tk.StringVar()
databasePath = ""

hltModule = StringVar()
hltTracker = StringVar()
hltTrackerActive = StringVar()
selectedTracker = StringVar()

trackerArr = []
trackerNameArr = []

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


def update_trackers(trackers):
    for tracker in trackers:
        tracker.update_position()
    sleep(0.001)


def new_database():
    global databasePath, databasePathVar
    config = configparser.ConfigParser()
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
    config.read("config")
    config.set("database", "path", path)
    with open("config", "w") as f:
        config.write(f)


def open_database():
    global databasePath, databasePathVar
    config = configparser.ConfigParser()
    path = filedialog.askopenfilename(
        initialdir=".",
        title="Open database",
        filetypes=[("database files", ".db"), ("all files", ".*")],
    )

    if path == "":
        return None

    databasePath = path
    databasePathVar.set("Database is: " + path)
    config.read("config")
    config.set("database", "path", path)
    with open("config", "w") as f:
        config.write(f)

def refresh_trackers(db):
    global trackerArr, trackerNameArr
    trackerArr = db.get_tracker_list()
    trackerNameArr = []
    for tracker in trackerArr:
        trackerNameArr.append(tracker.name)
    trackerNameArr.sort()

    trackerDropdown["menu"].delete(0,"end")
    for tracker in trackerNameArr:
        trackerDropdown["menu"].add_command(
            label=tracker, command=tk._setit(selectedTracker, tracker)
    )

def manage_trackers(db):
    i = None

    # Create window
    trackerWindow = tk.Toplevel(root)
    trackerWindow.title("Manage Trackers")
    trackerWindow.grab_set()

    # Tracker list
    trackerList = tk.Listbox(trackerWindow)
    trackerList.grid(row=1, rowspan=5, padx=10, pady=10, sticky=E + W)

    for index, tracker in enumerate(trackerNameArr, start=0):
        if tracker == selectedTracker.get():
            i = index
        trackerList.insert(index, tracker)

    # tracker renaming
    trackerNameLabel = tk.Label(trackerWindow, text="Rename tracker:")
    trackerNameLabel.grid(row=2, column=1, sticky=E + W)
    newTrackerName = tk.Entry(trackerWindow)
    newTrackerName.grid(row=2, column=2, sticky=E + W)

    acceptName = tk.Button(
        trackerWindow,
        text="Ok",
        command=lambda: update_tracker_list(db, trackerList, newTrackerName),
    )
    acceptName.grid(row=2, column=3)


def update_tracker_list(db, trackerList, name):
    i = trackerList.curselection()
    rename(trackerList, name)

    refresh_trackers(db)

    trackerList.delete(0,"end")
    for index, trackerName in enumerate(trackerNameArr, start=0):
        trackerList.insert(index, trackerName)


def rename(nameList, name):
    i = nameList.curselection()
    if i is None:
        return None
    for tracker in trackerArr:
        if tracker.name == nameList.get(i[0]):
            tracker.rename(str(name.get()))
    



def updateModuleSelect(event, database):
    if moduleList.curselection():
        hltModule.set(moduleList.get(moduleList.curselection()))
        checkButtonStatus.set(database.get_tracking_status(hltModule.get()))
    else:
        hltModule.set("")


def trackerSelect(*args):
    # Check in DB where name is located
    hltTracker.set("this is " + selectedTracker.get())
    print(selectedTracker.get())
    """TODO: Assign selected tracker to highlighted module"""


def toggleTracking(database):
    print("activated")
    print(checkButtonStatus.get())
    database.set_module_tracking_status(hltModule.get(), checkButtonStatus.get())


def testTread(databasePath, vr):
    database = Database(databasePath, vr)
    trackerList = database.get_tracker_list()
    while threading.main_thread().isAlive():
        update_trackers(trackerList)


if __name__ == "__main__":
    vr = triad_openvr.triad_openvr()
    vr.print_discovered_objects()

    config = configparser.ConfigParser()
    try:
        config.read("config")
        databasePath = config.get("database", "path")
    except configparser.NoSectionError:
        databasePath = filedialog.askopenfilename()
        if databasePath is "":
            exit_program()
        config.add_section("database")
        config.set("database", "path", databasePath)
        with open("config", "w") as f:
            config.write(f)

    databasePathVar.set("Database is: " + databasePath)
    database = Database(databasePath, vr)

    search_for_tracker(vr)

    trackerArr = database.get_tracker_list()
    for tracker in trackerArr:
        trackerNameArr.append(tracker.name)
    trackerNameArr.sort()

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
    trackerMenu.add_command(label="Refresh", command=lambda: refresh_trackers(database))
    trackerMenu.add_command(label="Manage Trackers", command=lambda: manage_trackers(database))

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
    selectedTracker.set("Choose tracker")
    selectedTracker.trace("w", trackerSelect)
    trackerDropdown = tk.OptionMenu(root, selectedTracker, *trackerNameArr)
    trackerDropdown.config(bg="white", fg="black")
    trackerDropdown["menu"].config(bg="white", fg="black")
    trackerDropdown.grid(row=2, column=1, columnspan=2)

    # Tracker serial label
    hltTracker.set("No tracker chosen")
    trackerSerial = tk.Label(root, bg="white", relief=RIDGE, textvariable=hltTracker)
    trackerSerial.grid(row=3, column=1, columnspan=2)

    # Tracker active
    hltTrackerActive.set("No tracker chosen")
    trackerActive = tk.Label(root, bg="white", relief=RIDGE, textvariable=hltTrackerActive)
    trackerActive.grid(row=4, column=1, columnspan=2, sticky=N)

    # Checkbox for using tracker on module
    trackerCheckbox = tk.Checkbutton(
        root,
        text="Track module?",
        var=checkButtonStatus,
        command=lambda: toggleTracking(database),
    )
    trackerCheckbox.grid(row=5, column=1, sticky=N, columnspan=2)

    # Create and run thread & GUI
    test = Thread(target=testTread, args=[databasePath, vr])
    test.start()

    root.mainloop()

