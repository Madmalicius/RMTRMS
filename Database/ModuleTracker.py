import tkinter as tk
from tkinter import *
import configparser
import createDatabase


root = tk.Tk()

root.title("Module Manager")

databasePathVar = tk.StringVar()
databasePath = ""


def new_database():
    global databasePath, databasePathVar
    path = filedialog.asksaveasfilename(
        initialdir=".",
        title="Create new database",
        filetypes=[("db files", ".db"), ("all files", ".*")],
    )

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
    databasePath = path
    databasePathVar.set("Database is: " + path)


def manage_trackers():
    # Create window
    trackerWindow = tk.Toplevel()
    trackerWindow.title("Manage Trackers")

    moduleList = tk.Listbox(trackerWindow)
    moduleList.grid(row=1, rowspan=5, padx=10, pady=10, sticky=E + W)
    moduleList.insert(1, "Machine 1")
    moduleList.insert(2, "Machine 2")
    moduleList.insert(3, "Machine 3")

    # tracker renaming
    trackerNameLabel = tk.Label(trackerWindow, text="Rename tracker:")
    trackerNameLabel.grid(row=2, column=1, sticky=E + W)
    trackerName = tk.Entry(trackerWindow)
    trackerName.grid(row=2, column=2, sticky=E + W)

    acceptName = tk.Button(trackerWindow, text="Ok", command=rename)
    acceptName.grid(row=2, column=3)


def rename():
    i = moduleList.curselection()
    if i:
        moduleList.delete(i)
        moduleList.insert(i, trackerName.get())


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
    databasePathWidget.grid(columnspan=4, sticky=E + W)

    # List of known modules
    moduleList = tk.Listbox(root)
    moduleList.grid(row=1, rowspan=5, padx=10, pady=10, sticky=E + W)
    moduleList.insert(1, "Machine 1")
    moduleList.insert(2, "Machine 2")
    moduleList.insert(3, "Machine 3")

    # Checkbox for using tracker on module
    trackerCheckbox = tk.Checkbutton(root, text="Track module?")
    trackerCheckbox.grid(row=3, column=1, sticky=N + E + W)

    root.mainloop()
