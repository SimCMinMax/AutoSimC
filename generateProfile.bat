@echo off
where /q python.exe
IF ERRORLEVEL 1 (
   ECHO Python.exe is missing. Ensure it is installed.
   pause
) ELSE (
    ECHO Python.exe exists. Launching AutoSimC Profile generator!
    ECHO --If you get the message: "cant open file "generateProfiles.py" [Errno2].."
    ECHO --Please add Python-Path to your Systemvariables-Path-Variable
    Echo --https://i.imgur.com/KM132c7.png
   python.exe generateProfiles.py -c priest -s shadow
   pause
)