# RTRMS

Realtime Module Tracking for Reconfigurable Manufacturing Systems

## Software Requirements

- Windows
- Siemens Tecnomatics
- SteamVR
- Python
- pipenv

## Setting up environment

Your computer must have both Siemens Tecnomatics and SteamVR installed.\
Students can download Siemens Tecnomatics for free from their [website](https://www.plm.automation.siemens.com/plmapp/education/plant-simulation/en_us/free-software/student/).\
SteamVR can be found under the <b>Tools</b> section of your Steam library.\
Python should be downloaded and installed from their [website](https://www.python.org/). The newest version (or most versions 3.x) will work.\
Once python is installed, use Pip to install pipenv:\
`python -m pip install pipenv`\
Clone this repository using Git:\
`git clone https://github.com/madmalicius/RMTRMS.git`\
Navigate to the repository and to the Database folder: \
`cd RMTRMS/Database`\
Install the necessary Python packages:\
`python -m pipenv install`\
Activate the virtual environment:\
`python -m pipenv shell`\
Create the database by running the script:\
`python createDatabase.py`

## Setting up SteamVR to run HMD-less

[Triad Semi](http://help.triadsemi.com/steamvr-tracking/steamvr-tracking-without-an-hmd) has a great guide on how to run SteamVR without a headset. <b>To summarize:</b>

Run SteamVR and set up your playspace as normal. After this is done, close SteamVR.\
Modify the following files:

- (<Steam Directory>/steamapps/common/SteamVR/drivers/null/resources/settings/default.vrsettings)\
  Change the following lines:\
  "enable" : true

- (<Steam Directory>/config/steamvr.vrsettings)\
  Add the following lines under the "steamvr" section:\
  "requireHmd" : false\
  "forcedDriver" : "null"\
  "activateMultipleDrivers" : true

After this, you should be able to unplug the headset and box and run SteamVR using only the tracker and accompanying dongle.

<b>NOTE</b>\
SteamVR may give errors such as "Compositor is not running", "room setup is invalid", but these will not effect the system.

## Setting up Siemens Tecnomatix

To setup the Tecnomatix simulation, create a new model with the following components:

```
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
- Method        : endSim
- Method        : dbOpen
- Method        : dbClose
- Method        : listModules
- Method        : moveModules
- Method        : updatePosition
- Method        : updateModules

User Objects
- Frame         : <module name>
(Add in more frames if needed)
```

The content of the method files can be found under [MethodFiles](/Tecnomatix/MethodFiles).

Add a connector between `Source` and `SingleProc`, and between `SingleProc` and `Drain`. double-click `Drain` and under control>Entrance select `moveModules`. In methods `dbOpen`, `dbClose` and `moveModules` change the path of commands where instructed.

Lastly, click the _Home>Navigate>Open 2D/3D_ button.

## Running the program

Open the project in Siemen Tecnomatix and allow access to your computer. Double click the PositionDB block and change the file location to the newly created database. You should also enable "ignore errors" in the debugger tab.\
Run the updatePosition script:\
`python updatePosition.py`\
The position should now be updating and shown in the console. Start the simulation in Tecnomatix.
