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
from configure import configure, SteamVRRunningError as configureError
from restore import restore, SteamVRRunningError as restoreError

bgColor = "#B0C4DE"

root = tk.Tk()

root.title("Module Manager")
root.config(bg=bgColor)

databasePathVar = tk.StringVar()
databasePath = ""

# Variables for root window
hltModule = StringVar()
hltTracker = StringVar()
hltTrackerActive = StringVar()
selectedTracker = StringVar()
checkButtonStatus = IntVar()
updateThreadListFlag = False

#Variables for tracker window
hltTrackerActiveInManager = StringVar()
hltTrackerModuleAssigned = StringVar()
newName = StringVar()

trackerArr = []
trackerNameArr = []

def update_trackers(trackers):
    """Updates the position of active trackers and saves it to the database.

    arguments:
        trackers {array} -- Array of trackers from the database.
    """
    for tracker in trackers:
        tracker.update_position()
    sleep(0.001)


def new_database():
    """Creates a new database file."""
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
    """Opens a database file."""
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


def refresh_trackers(db, triggerWarning=False):
    """reloads all known trackers from the database.
    
    Arguments:
        db {Database} -- The object linked to the current database connection.
        triggerWarning {bool} -- If a warning window should open if no trackers are found in the database. Optional, default is no warning.
    """
    global trackerArr, trackerNameArr
    trackerArr = db.get_tracker_list()
    if triggerWarning:
        if trackerArr:
            updateThreadListFlag = True
        else:
            tk.messagebox.showwarning(
                "No trackers",
                "No trackers found in database. Use the refresh button scan for trackers",
            )
    trackerNameArr = []
    for tracker in trackerArr:
        trackerNameArr.append(tracker.name)
        if tracker.name == selectedTracker.get():
            if tracker.active:
                hltTrackerActive.set("Active")
            else:
                hltTrackerActive.set("Inactive")
    trackerNameArr.sort()

    trackerDropdown["menu"].delete(0, "end")
    for tracker in trackerNameArr:
        trackerDropdown["menu"].add_command(
            label=tracker, command=tk._setit(selectedTracker, tracker)
        )


def manage_trackers(db):
    """Creates a new window for tracker management.
    
    Arguments:
        db {Database} -- The object linked to the current database connection.
    """
    i = None

    # Create window
    trackerWindow = tk.Toplevel(root, bg=bgColor)
    trackerWindow.title("Manage Trackers")
    trackerWindow.grab_set()

    # Tracker list label
    trackerListLabel = tk.Label(trackerWindow, text="Trackers", bg=bgColor, font=11)
    trackerListLabel.grid(sticky=E)

    # Refresh Trackers button
    refreshTrackers = tk.Button(trackerWindow, text="↻", command=lambda: update_tracker_list(db, trackerList))
    refreshTrackers.grid(row=0, column=1, sticky=S+E, pady=10, padx=10)
    
    # Tracker list
    trackerList = tk.Listbox(trackerWindow)
    trackerList.bind("<ButtonRelease-1>", lambda event: updateTrackerSelect(event, db, trackerList, removeTrackerButton, acceptName))
    trackerList.grid(row=1, rowspan=5, columnspan=2, padx=10, pady=5, sticky=E + W)

    for index, tracker in enumerate(trackerNameArr, start=0):
        if tracker == selectedTracker.get():
            i = index
        trackerList.insert(index, tracker)

    # tracker renaming
    newName.set("")
    newName.trace("w", lambda *args: enableOkButton(*args, trackerList=trackerList, okBtn=acceptName))
    trackerNameLabel = tk.Label(trackerWindow, text="Rename tracker:", bg=bgColor)
    trackerNameLabel.grid(row=2, column=2, sticky=E + W, padx=5)
    newTrackerName = tk.Entry(trackerWindow, textvariable=newName)
    newTrackerName.grid(row=2, column=3, sticky=E + W)

    acceptName = tk.Button(
        trackerWindow,
        text="Ok",
        command=lambda: update_tracker_list(db, trackerList, newTrackerName),
        state=DISABLED
    )
    acceptName.grid(row=2, column=4, padx=5)

    # Remove tracker
    removeTrackerButton = tk.Button(
        trackerWindow, text="Remove", command=lambda: removeTracker(db, trackerList, newTrackerName, removeTrackerButton), state=DISABLED
    )
    removeTrackerButton.grid(row=3, column=3, sticky=N)

    # Assigned module
    hltTrackerModuleAssigned.set("Select tracker")
    assignedModule = tk.Label(trackerWindow, bg="white", relief=RIDGE, textvariable=hltTrackerModuleAssigned)
    assignedModule.grid(row=4, column=3, sticky=W)
    assignedModuleLabel = tk.Label(trackerWindow, text="Assigned module:", bg=bgColor)
    assignedModuleLabel.grid(row=4, column=2, sticky=E, padx=5)

    # Tracker status
    hltTrackerActiveInManager.set("Select tracker")
    trackerStatus = tk.Label(trackerWindow, bg="white", relief=RIDGE, textvariable=hltTrackerActiveInManager)
    trackerStatus.grid(row=5, column=3, sticky=W)
    trackerStatusLabel = tk.Label(trackerWindow, text="tracker status:", bg=bgColor)
    trackerStatusLabel.grid(row=5, column=2, sticky=E, padx=5)

def enableOkButton(*args, trackerList, okBtn):
    if trackerList.curselection():
        if newName.get():
            okBtn.config(state=NORMAL)
        else:
            okBtn.config(state=DISABLED)

def removeTracker(db, trackerList, nameEntry, rmvBtn):
    """Removes tracker from database.
    
    Arguments:
        db {Database} -- The object linked to the current database connection.
        trackerList {Listbox} -- List of tracker names.
    """
    rmvBtn.config(state=DISABLED)

    if nameEntry:
        nameEntry.delete(0,END)
        
    
    if trackerList.curselection():
        for tracker in trackerArr:
            if tracker.name == trackerList.get(trackerList.curselection()):
                if tracker.name == selectedTracker.get():
                    selectedTracker.set("Select tracker")
                db.remove_tracker(tracker)
        update_tracker_list(db, trackerList)


def update_tracker_list(db, trackerList, name=None):
    """Refreshes the list of trackers.
    
    Arguments:
        db {Database} -- The object linked to the current database connection.
        trackerList {Listbox} -- list of tracker names.
        name {string} -- New desired name for highlighted tracker. Optional, default is no name.
    """
    i = trackerList.curselection()

    if name:
        rename(db, trackerList, name)
        name.delete(0,END)

    refresh_trackers(db)

    hltTrackerActiveInManager.set("Select tracker")
    hltTrackerModuleAssigned.set("Select tracker")

    trackerList.delete(0, "end")
    for index, trackerName in enumerate(trackerNameArr, start=0):
        trackerList.insert(index, trackerName)


def rename(db, nameList, name):
    """Renames the highlighted tracker.
    
    Arguments:
        db {Database} -- The object linked to the current database connection.
        nameList {Listbox} -- List of tracker names.
        name {string} -- New desired name.
    """
    i = nameList.curselection()
    if not i:
        return None
    for tracker in trackerArr:
        if tracker.name == nameList.get(i[0]):
            print(tracker.name + " " + selectedTracker.get())
            if tracker.name == selectedTracker.get():
                tracker.rename(str(name.get()))
                selectedTracker.set(name.get())
                enableApplyButton(db)
            else:
                tracker.rename(str(name.get()))


def updateModuleSelect(event, database):
    """Updates the labels in the root window.
    
    Arguments:
        event {event} -- Event handler.
        database {Database} -- The object linked to the current database connection.
    """
    if moduleList.curselection():
        hltModule.set(moduleList.get(moduleList.curselection()))
        checkButtonStatus.set(database.get_tracking_status(hltModule.get()))
        assignedTracker = database.get_assigned_tracker(hltModule.get())
        if assignedTracker:
            selectedTracker.set(assignedTracker.name)
        else:
            selectedTracker.set("Select tracker")
        enableApplyButton(database)
    else:
        hltModule.set("")
    

def updateTrackerSelect(event, database, trackerList, rmvBtn, okBtn):
    """Updates the labels in the Manage Trackers window.
    
    Arguments:
        event {event} -- Event handler.
        database {Database} -- The object linked to the current database connection.
    """
    rmvBtn.config(state=NORMAL)
    newName.set("")
    refresh_trackers(database)
    for tracker in trackerArr:
        if tracker.name == trackerList.get(trackerList.curselection()):
            hltTrackerModuleAssigned.set(database.get_assigned_module(tracker))
            if tracker.active:
                hltTrackerActiveInManager.set("Active")
            else:
                hltTrackerActiveInManager.set("Inactive")


def trackerSelect(*args, db):
    """Shows serial and status of the selected tracker.
    
    Arguments:
        *args {args} -- Required argument list for stringVar tracing.
        db {Database} -- The object linked to the current database connection.
    """
    # Check in DB where name is located
    enableApplyButton(db)
    hltTracker.set("No Tracker Assigned")
    hltTrackerActive.set("No Tracker Assigned")
    refresh_trackers(db)
    for tracker in trackerArr:
        if tracker.name == selectedTracker.get():
            hltTracker.set(tracker.serial)
            if tracker.active:
                hltTrackerActive.set("Active")
            else:
                hltTrackerActive.set("Inactive")


def toggleTracking(database):
    """Saves the chosen tracking status of the highlighted module.
    
    Arguments:
        database {Database} -- The object linked to the current database connection.
    """
    print("activated")
    print(checkButtonStatus.get())
    database.set_module_tracking_status(hltModule.get(), checkButtonStatus.get())


def assignTrackerToModule(database):
    """Assigns the chosen tracker to the highlighted module.
    
    Arguments:
        database {Database} -- The object linked to the current database connection.
    """
    for tracker in trackerArr:
        if tracker.name == selectedTracker.get():
            database.assign_tracker(hltModule.get(), tracker)


def saveChanges(database):
    """Saves current changes to the database.
    
    Arguments:
        database {Database} -- The object linked to the current database connection.
    """
    if not database.get_tracking_status(hltModule.get()) == checkButtonStatus.get():
        toggleTracking(database)

    if database.get_assigned_tracker(hltModule.get()):
        if (
            not database.get_assigned_tracker(hltModule.get()).name
            == selectedTracker.get()
        ):
            assignTrackerToModule(database)
    else:
        assignTrackerToModule(database)
    applyButton.config(state=DISABLED)


def enableApplyButton(db):
    """Checks if the apply button should be enabled.

    Arguments:
        db {Database} -- The object linked to the current database connection.
    """
    if hltModule.get():
        if db.get_assigned_tracker(hltModule.get()):
            if (
                not db.get_assigned_tracker(hltModule.get()).name
                == selectedTracker.get()
                or not db.get_tracking_status(hltModule.get())
                == checkButtonStatus.get()
            ):
                applyButton.config(state=NORMAL)
            else:
                applyButton.config(state=DISABLED)
        elif not selectedTracker.get() == "Select tracker":
            applyButton.config(state=NORMAL)
        else:
            applyButton.config(state=DISABLED)


def trackerPositionThread(databasePath, vr):
    """Thread function: Creates new link to the database and tracker list.

    Arguments:
        databasePath {string} -- Path to the designated database file.
        vr {triad_openvr} -- vr object.
    """
    global updateThreadListFlag
    database = Database(databasePath, vr)
    trackerList = database.get_tracker_list()
    while threading.main_thread().isAlive():
        if updateThreadListFlag:
            trackerList = database.get_tracker_list()
            updateThreadListFlag = False
        update_trackers(trackerList)


def configureSteamVR():
    """Configures the SteamVR settings to run in headless mode."""
    try:
        configure()
    except configureError:
        tk.messagebox.showerror(
            "SteamVRRunningError",
            "Cannot modify files while SteamVR is running. Please close the program and try again.",
        )


def restoreSteamVR():
    """Restores the setting in SteamVR to default."""
    try:
        restore()
    except restoreError:
        tk.messagebox.showerror(
            "SteamVRRunningError",
            "Cannot modify files while SteamVR is running. Please close the program and try again.",
        )


if __name__ == "__main__":
    try:
        vr = triad_openvr.triad_openvr()
    except OpenVRError as e:
        print(e)
        print("\r\n Error: Please install SteamVR")
        if tk.messagebox.showerror(
            "SteamVR Error", "SteamVR not found. Please install SteamVR"
        ):
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

    trackerArr = database.get_tracker_list()
    if trackerArr:
        for tracker in trackerArr:
            trackerNameArr.append(tracker.name)
        trackerNameArr.sort()
    else:
        trackerNameArr.append("No trackers found")
        tk.messagebox.showwarning(
            "No trackers",
            "No trackers found in database. Use the refresh button scan for trackers",
        )

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
    trackerMenu.add_command(
        label="Refresh", command=lambda: refresh_trackers(database, True)
    )
    trackerMenu.add_command(
        label="Manage Trackers", command=lambda: manage_trackers(database)
    )

    # Add subtabs to vrMenu
    vrMenu.add_command(label="Configure", command=configureSteamVR)
    vrMenu.add_command(label="Restore", command=restoreSteamVR)

    # Add help & About buttons
    menu.add_command(
        label="Help",
        command=lambda: webbrowser.open_new_tab(
            "https://github.com/Madmalicius/RMTRMS/wiki/For-Users#using-the-gui"
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
    moduleName.grid(row=1, rowspan=2, column=1, columnspan=2, sticky=E + W + S)

    # Tracker choice
    selectedTracker.set("No module chosen")
    selectedTracker.trace("w", lambda *args: trackerSelect(*args, db=database))
    trackerDropdown = tk.OptionMenu(root, selectedTracker, *trackerNameArr)
    trackerDropdown.config(bg="white", fg="black")
    trackerDropdown["menu"].config(bg="white", fg="black")
    trackerDropdown.grid(row=3, column=1, columnspan=2)
    trackerDropdown["menu"].delete(0, "end")

    # Tracker serial label
    hltTracker.set("No module chosen")
    trackerSerial = tk.Label(root, bg="white", relief=RIDGE, textvariable=hltTracker)
    trackerSerial.grid(row=4, column=2, sticky=W)

    trackerSerialLabel = tk.Label(root, text="Serial:", bg=bgColor)
    trackerSerialLabel.grid(row=4, column=1, sticky=E)

    # Tracker active
    hltTrackerActive.set("No module chosen")
    trackerActive = tk.Label(
        root, bg="white", relief=RIDGE, textvariable=hltTrackerActive
    )
    trackerActive.grid(row=5, column=2, sticky=N + W)

    trackerActiveLabel = tk.Label(root, text="Status:", bg=bgColor)
    trackerActiveLabel.grid(row=5, column=1, sticky=N + E)

    # Checkbox for using tracker on module
    trackerCheckbox = tk.Checkbutton(
        root,
        text="Track module?",
        var=checkButtonStatus,
        command=lambda: enableApplyButton(database),
    )
    trackerCheckbox.grid(row=1, rowspan=2, column=3, sticky=S)

    # Apply button
    applyButton = tk.Button(
        root, text="Apply", command=lambda: saveChanges(database), state=DISABLED
    )
    applyButton.grid(row=5, column=3, sticky=N)

    # Create and run thread & GUI
    trackerPosition = Thread(
        target=trackerPositionThread, args=[databasePath, vr], daemon=False
    )
    trackerPosition.start()

    root.mainloop()

    database.db.close()
