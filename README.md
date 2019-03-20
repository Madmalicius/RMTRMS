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

## Running the program

Open the project in Siemen Tecnomatix and allow access to your computer. Double click the PositionDB block and change the file location to the newly created database. You should also enable "ignore errors" in the debugger tab.\
Run the updatePosition script:\
`python updatePosition.py`\
The position should now be updating and shown in the console. Start the simulation in Tecnomatix.

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
