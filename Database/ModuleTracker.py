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


def change_name():
    i = moduleList.curselection()
    if i:
        moduleList.delete(i)
        moduleList.insert(i, moduleName.get())


if __name__ == "__main__":
    menu = tk.Menu(root)

    root.config(menu=menu)

    filemenu = tk.Menu(menu)

    menu.add_cascade(label="File", menu=filemenu)

    filemenu.add_command(label="Create database", command=new_database)
    filemenu.add_command(label="Open database", command=open_database)

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

    # Module renaming
    moduleNameLabel = tk.Label(root, text="Rename module")
    moduleNameLabel.grid(row=2, column=1, sticky=E + W)
    moduleName = tk.Entry(root)
    moduleName.grid(row=2, column=2, sticky=E + W)

    acceptName = tk.Button(root, text="Ok", command=change_name)
    acceptName.grid(row=2, column=3)

    # Checkbox for using tracker on module
    trackerCheckbox = tk.Checkbutton(root, text="Track module?")
    trackerCheckbox.grid(row=3, column=1, sticky=N + E + W)

    root.mainloop()
