import tkinter as tk
from tkinter import filedialog
import configparser
import createDatabase


root = tk.Tk()

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
    except configparser.NoSectionError:
        open_database()
        config.add_section("database")
        config.set("database", "path", databasePath)

    databasePathWidget = tk.Label(root, textvariable=databasePathVar)
    databasePathWidget.pack()

    root.mainloop()
