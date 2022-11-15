# cpu_util_port_analyzer

cpu port util analyzer is a tool which is used to get the visualization how the cpu, memory, docker, temperature is being used. This basically creates graphs, csv files, text files etc.

# How it works

Step 1 : It makes remote SSH session with the device with the help of NETMIKO (python libarary used to make SSH connection).
Step 2 : Taking snapshots of varoius commands timely.
Step 3 : Extracting required data from snapshots to make graphs, csv file, text files etc.
Step 4 : plots graphs, makes csv files, makes text files and gives us an output.

# prerequisit before running the tool

1. It needs an IP address, username , password of the device which you wnat to work with.
2. The device should be accessable.
3. You need some pacakages to be install which [are mentioned in the requirement.txt file.

# INPUT

1. IP address of the device
2. Username
3. Password
4. Email ID (where you get the alerts)
5. Number of snapshots you want to take.







python script should be run in the Sonic device in background to fetch data for time based data-
points which in turn should be stored in an excel sheet for further analysis. If, there are any performace
concerns due the script running in background, the script can fetch the required output from outside the
device. The CLI commands are explained below:
The below commands is used to determine the CPU utilization. It also lists the active processes along
with their corresponding process ID and other relevant parameters.
This sub-section explains the various &quot;processes&quot; specific data that includes the following.
1. cpu Show processes CPU info
2. memory Show processes memory info
3. summary Show processes info
“show processes” commands provide a wrapper over linux’s “top” command. “show process cpu” sorts
the processes being displayed by cpu-utilization, whereas “show process memory” does it attending to
processes’ memory-utilization.
