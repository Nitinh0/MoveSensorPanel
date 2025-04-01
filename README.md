I am not a programmer and don’t have much knowledge of Python, but with a lot of help from ChatGPT, I created this small project.

The goal of the program is to move the AIDA64 sensor panel to a specific monitor and keep it there, even if there are changes in the monitor setup or if moved for some reason. Once the "Pin to Monitor" feature from AIDA64 doesn’t work properly for me when I disconnect one of my monitors or suspend Windows...

changelog:
Since the panel can be locked on Aida and it only change position when there is a change on the monitors configuration, there is no need to keep a loop always checking it. instead now it will look for windows events to trigger the program and move the panel.

Feel free to check the code and give it a try
[Release](https://github.com/Nitinh0/MoveSensorPanel/releases/tag/v1.1)
