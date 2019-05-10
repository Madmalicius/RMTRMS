# RTRMS

Realtime Module Tracking for Reconfigurable Manufacturing Systems

## Setting up the system

### Software Requirements

- Windows
- Git
- Siemens Tecnomatics
- SteamVR
- Python
- pipenv

### Setting up environment

Your computer must have both Siemens Tecnomatics and SteamVR installed.

Students can download Siemens Tecnomatics for free from their [website](https://www.plm.automation.siemens.com/plmapp/education/plant-simulation/en_us/free-software/student/).

SteamVR can be found under the <b>Tools</b> section of your Steam library.

The newest version of Git for Windows can be found [here](https://gitforwindows.org/).

Python should be downloaded and installed from their [website](https://www.python.org/). The newest version (or most versions 3.x) will work.
For CMD, the path to Python might need to be added manually. A guide can be found [here](https://edu.google.com/openonline/course-builder/docs/1.10/set-up-course-builder/check-for-python.html).

Once python is installed, use Pip to install pipenv in either CMD, Git Bash or PowerShell:\
`python -m pip pipenv sync`

In CMD, Git Bash or PowerShell, cd into your work directory and clone this repository using Git:\
`git clone https://github.com/madmalicius/RMTRMS.git`

Navigate to the repository and to the Database folder:\
`cd RMTRMS/Database`

Install the necessary Python packages:\
`python -m pipenv install`

Activate the virtual environment:\
`python -m pipenv shell`

Create the database by running the script:\
`python createDatabase.py`

### Setting up SteamVR to run HMD-less

[Triad Semi](http://help.triadsemi.com/steamvr-tracking/steamvr-tracking-without-an-hmd) has a great guide on how to run SteamVR without a headset.

For your convenience, we've created a script to automatically set this up.:

Run SteamVR and set up your playspace as normal. After this is done, close SteamVR.

Run the python script `configure.py` found in the SteamVR folder in this repository. This will copy the settings file to your steam directory (Assuming default Steam install directory).

Alternatively, you can copy and paste the file into your Steam/config directory.

After this, you should be able to unplug the headset and box and run SteamVR using only the tracker and accompanying dongle.

<b>NOTE</b>\
SteamVR may give errors such as "Compositor is not running", "room setup is invalid", but these will not effect the system.

### Setting up Siemens Tecnomatix

To setup the Tecnomatix simulation, create a new 2D model with the following components:

```
<Toolbox tab>
- <Component>   : <Component Name>

Material Flow
- Source        : Source
- SingleProc    : SingleProc
- Drain         : Drain

Information Flow
- TableFile     : modules
- TableFile     : trackerPosition
- SQLite        : positionDB
- Method        : INIT
- Method        : RESET
- Method        : ENDSIM
- Method        : dbOpen
- Method        : dbClose
- Method        : listModules
- Method        : moveModules
- Method        : updatePosition
- Method        : updateModules

User Objects
- Frame         : <Module Name>
(Add in more frames if needed)

```

SQLite can be added to the toolbox through _home>Model>Manage Class Library_ under _Basic Objects>Information Flow_.

The content of the method files can be found under [MethodFiles](/Tecnomatix/MethodFiles).

Right-click component and click _Rename_ to name the component.

Add a connector between `Source` and `SingleProc`, and between `SingleProc` and `Drain`. Double-click `Drain` and under _Controls>Entrance_ select `moveModules`.

In methods `dbOpen`, `dbClose` and `moveModules` change the path of commands where instructed.

Tecnomatix needs access to the computer. This is given by going to _File>Model Settings>general_ and uncheck `Prohibit access to the computer`

Lastly, click the _Home>Navigate>Open 2D/3D_ button, accept the default 3D graphics.

Run the simulation by clicking _Home>Event Controller>Start/stop Simulation_.

## Using the GUI

Running the GUI gives the opportunity to assign and manage trackers to modules created in Tecnomatix.

### Main Window Interface

On the main window, the list on the left side shows all modules created in Tecnomatix. This list includes _User Object Frames_ and _Single Procs_.

The white label in the middle of the GUI displays the name of the selected module from the list.

Above the label, the path to the currently loaded database file is shown.

Underneath is a dropdown menu of all trackers available to be assigned to the selected module.

The checkbox on the right side of the module label determines whether or not the specific module should be tracked in Tecnomatix.

The Apply button assigns the current chosen tracker to the highlighted module along with changing the tracking status depending on the checkbox status.

### Menu Options

The GUI interface has several top menu options as well.

**File**: With subtabs _Create Database_ and _Open Database_.

- Create Database: creates a new SQLite database file and sets the path to the new file.
- Open Database: load in an existing SQLite database file.

**Trackers**: With subtabs _Refresh_ and _Manage Trackers_.

- Refresh: Reloads the list of known trackers from the database.
- Manage Trackers: Opens a new window for tracker management. See [Manage Trackers Window](#Manage-Trackers-Window).

**SteamVR**: With subtabs _Configure_ and _Restore_.

- Configure: Sets up SteamVR to run in headless mode so only lighthouses and trackers are needed.
- Restore: Reverts SteamVR back to the default settings.

**Help**: Opens the help page on Github.

**About**: Opens the About page on Github.

### Manage Trackers Window

The Manage Trackers window shows a list of all known trackers with the ability to rename or delete them from the database.

The desired name is entered into the textfield and the tracker to be renamed should be highlighted on the list to the left. The _Ok_ button saves the new name for the tracker in the database.
