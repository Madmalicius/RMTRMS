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

[Triad Semi](http://help.triadsemi.com/steamvr-tracking/steamvr-tracking-without-an-hmd) has a great guide on how to run SteamVR without a headset. \

For your convenience, we've created a script to automatically set this up.:

Run SteamVR and set up your playspace as normal. After this is done, close SteamVR.

Run the python script `configure.py` found in the SteamVR folder in this repository. This will copy the settings file to your steam directory (Assuming default Steam install directory).

Alternatively, you can copy and paste the file into your Steam/config directory.

After this, you should be able to unplug the headset and box and run SteamVR using only the tracker and accompanying dongle.

<b>NOTE</b>\
SteamVR may give errors such as "Compositor is not running", "room setup is invalid", but these will not effect the system.

## Setting up Siemens Tecnomatix

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
