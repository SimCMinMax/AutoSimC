@echo off
where /q python.exe
IF ERRORLEVEL 1 (
   ECHO Python.exe is missing. Ensure it is installed and placed in your PATH.
   timeout 10
   EXIT /B
) ELSE (
    ECHO Python.exe exists. Launching AutoSimC!
   python.exe main.py -i input.txt -o out.simc -quiet -sim stage1
   pause
)

REM For legendary permutations in command line, use this command :
REM python main.py -i settings.ini -o out.simc -l "leg1|id|bonus|enchant|gem,leg2|id2|bonus2|enchant2|gem2" 0:2