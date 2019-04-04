#!/usr/bin/env python
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import configparser
import createDatabase


root = tk.Tk()

root.title("Module Manager")
root.config(bg="#B0C4DE")

databasePathVar = tk.StringVar()
databasePath = ""
hltModule = StringVar()
hltTracker = StringVar()
trackers = StringVar()
trackerArr = []


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
    # Create window
    trackerWindow = tk.Toplevel(root)
    trackerWindow.title("Manage Trackers")
    trackerWindow.grab_set()

    # Tracker list
    trackerList = tk.Listbox(trackerWindow)
    trackerList.grid(row=1, rowspan=5, padx=10, pady=10, sticky=E + W)
    trackerList.insert(1, "Machine 1")
    trackerList.insert(2, "Machine 2")
    trackerList.insert(3, "Machine 3")

    # tracker renaming
    trackerNameLabel = tk.Label(trackerWindow, text="Rename tracker:")
    trackerNameLabel.grid(row=2, column=1, sticky=E + W)
    trackerName = tk.Entry(trackerWindow)
    trackerName.grid(row=2, column=2, sticky=E + W)

    acceptName = tk.Button(
        trackerWindow, text="Ok", command=lambda: rename(trackerList, trackerName)
    )
    acceptName.grid(row=2, column=3)


def rename(List, name):
    i = List.curselection()
    if i:
        print("woo!")
        List.delete(i)
        List.insert(i, name.get())
    else:
        print("nooo!")


def updateModuleSelect(event):
    if moduleList.curselection():
        hltModule.set(moduleList.get(moduleList.curselection()))
    else:
        hltModule.set("")


def trackerSelect(*args):
    # Check in DB where name is located
    if trackers.get() == "tracker 1":
        hltTracker.set("This is tracker 1")
    else:
        hltTracker.set("This is not tracker 1")
    print(trackers.get())


if __name__ == "__main__":
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
    moduleList.bind("<ButtonRelease-1>", updateModuleSelect)
    moduleList.grid(row=1, rowspan=5, padx=10, pady=10, sticky=N + S + W)
    moduleList.insert(1, "Machine 1")
    moduleList.insert(2, "Machine 2")
    moduleList.insert(3, "Machine 3")

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
    trackerCheckbox = tk.Checkbutton(root, text="Track module?")
    trackerCheckbox.grid(row=3, column=1, sticky=N + E + W)

    root.mainloop()
