#!/usr/bin/env python
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import threading
from threading import Thread
from time import sleep
import configparser
import triad_openvr
from openvr import OpenVRError
from RMTRMS import Database, Tracker
import os
import webbrowser
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/Database")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/SteamVR")
import createDatabase
from configure import configure
from restore import restore


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

    trackerDropdown["menu"].delete(0, "end")
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

    # Tracker list label
    trackerListLabel = tk.Label(trackerWindow, text="Trackers")
    trackerListLabel.grid(sticky=S)

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

    removeTrackerButton = tk.Button(
        trackerWindow, text="delete", command=lambda: removeTracker(db, trackerList)
    )


def removeTracker(db, trackerList):
    if trackerList.curselection():
        for tracker in trackerArr:
            if tracker.name == trackerList.get(trackerList.curselection()):
                db.remove_tracker(tracker)
        update_tracker_list(db, trackerList)


def update_tracker_list(db, trackerList, name=None):
    i = trackerList.curselection()

    if name:
        rename(trackerList, name)

    refresh_trackers(db)

    trackerList.delete(0, "end")
    for index, trackerName in enumerate(trackerNameArr, start=0):
        trackerList.insert(index, trackerName)


def rename(nameList, name):
    i = nameList.curselection()
    if not i:
        return None
    for tracker in trackerArr:
        if tracker.name == nameList.get(i[0]):
            tracker.rename(str(name.get()))


def updateModuleSelect(event, database):
    if moduleList.curselection():
        hltModule.set(moduleList.get(moduleList.curselection()))
        checkButtonStatus.set(database.get_tracking_status(hltModule.get()))
        assignedTracker = database.get_assigned_tracker(hltModule.get())
        if assignedTracker:
            selectedTracker.set(assignedTracker.name)
        else:
            selectedTracker.set("Choose tracker")
    else:
        hltModule.set("")


def trackerSelect(*args):
    # Check in DB where name is located
    hltTracker.set("No Tracker Assigned")
    for tracker in trackerArr:
        if tracker.name == selectedTracker.get():
            hltTracker.set(tracker.serial)


def toggleTracking(database):
    print("activated")
    print(checkButtonStatus.get())
    database.set_module_tracking_status(hltModule.get(), checkButtonStatus.get())


def assignTrackerToModule(database):
    for tracker in trackerArr:
        if tracker.name == selectedTracker.get():
            database.assign_tracker(hltModule.get(), tracker)


def saveChanges(database):
    toggleTracking(database)
    assignTrackerToModule(database)


def testTread(databasePath, vr):
    database = Database(databasePath, vr)
    trackerList = database.get_tracker_list()
    while threading.main_thread().isAlive():
        update_trackers(trackerList)


if __name__ == "__main__":
    try:
        vr = triad_openvr.triad_openvr()
        vr.print_discovered_objects()
    except OpenVRError as e:
        print(e)
        print("\r\n Error: Please install SteamVR")
        tk.messagebox.showerror(
            "SteamVR Error", "SteamVR not found. Please install SteamVR"
        )
        exit()
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
    vrMenu = tk.Menu(menu, tearoff=False)

    # Add tabs to Menu
    menu.add_cascade(label="File", menu=fileMenu)
    menu.add_cascade(label="Trackers", menu=trackerMenu)
    menu.add_cascade(label="SteamVR", menu=vrMenu)

    # Add subtabs to File
    fileMenu.add_command(label="Create database", command=lambda: new_database)
    fileMenu.add_command(label="Open database", command=lambda: open_database)

    # Add subtabs to Trackers
    trackerMenu.add_command(label="Refresh", command=lambda: refresh_trackers(database))
    trackerMenu.add_command(
        label="Manage Trackers", command=lambda: manage_trackers(database)
    )

    # Add subtabs to vrMenu
    vrMenu.add_command(label="Configure", command=configure)
    vrMenu.add_command(label="Restore", command=restore)

    # Add help & About buttons
    menu.add_command(
        label="Help",
        command=lambda: webbrowser.open_new_tab(
            "https://github.com/Madmalicius/RMTRMS/wiki/Using-the-GUI"
        ),
    )
    menu.add_command(
        label="About",
        command=lambda: webbrowser.open_new_tab(
            "https://github.com/Madmalicius/RMTRMS/graphs/contributors"
        ),
    )

    # Show path to active database
    databasePathWidget = tk.Label(root, textvariable=databasePathVar)
    databasePathWidget.grid(columnspan=4, sticky=E + W)

    # Module list label
    moduleListLabel = tk.Label(root, text="Modules", bg="#B0C4DE", font=10)
    moduleListLabel.grid(row=1, sticky=W + S, padx=20)

    # List of known modules
    moduleList = tk.Listbox(root)
    moduleList.bind(
        "<ButtonRelease-1>", lambda event: updateModuleSelect(event, database)
    )
    moduleList.grid(row=2, rowspan=4, padx=10, pady=5, sticky=N + S + W)
    modules = database.get_module_list()
    for index, module in enumerate(modules, start=0):
        moduleList.insert(index, module)

    # Highlighted module label
    moduleName = tk.Label(
        root, bg="white", relief=RIDGE, textvariable=hltModule, font=16
    )
    moduleName.grid(row=1, rowspan=2, column=1, sticky=E + W + S)

    # Tracker choice
    selectedTracker.set("Choose tracker")
    selectedTracker.trace("w", trackerSelect)
    trackerDropdown = tk.OptionMenu(root, selectedTracker, *trackerNameArr)
    trackerDropdown.config(bg="white", fg="black")
    trackerDropdown["menu"].config(bg="white", fg="black")
    trackerDropdown.grid(row=3, column=1)

    # Tracker serial label
    hltTracker.set("No module chosen")
    trackerSerial = tk.Label(root, bg="white", relief=RIDGE, textvariable=hltTracker)
    trackerSerial.grid(row=4, column=1)

    # Tracker active
    hltTrackerActive.set("No tracker chosen")
    trackerActive = tk.Label(
        root, bg="white", relief=RIDGE, textvariable=hltTrackerActive
    )
    trackerActive.grid(row=5, column=1, sticky=N)

    # Checkbox for using tracker on module
    trackerCheckbox = tk.Checkbutton(root, text="Track module?", var=checkButtonStatus)
    trackerCheckbox.grid(row=1, rowspan=2, column=2, sticky=S)

    # Apply button
    applyButton = tk.Button(root, text="Apply", command=lambda: saveChanges(database))
    applyButton.grid(row=5, column=2, sticky=N)

    # Create and run thread & GUI
    test = Thread(target=testTread, args=[databasePath, vr], daemon=False)
    test.start()

    root.mainloop()

    database.db.close()
