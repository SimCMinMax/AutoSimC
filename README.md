AutoSimC
========

Python script to create multiple profiles for SimulationCraft to find Best-in-Slot and best enchants/gems/talents combinations.

Don't hesitate to go on the [SimcMinMax](https://discordapp.com/invite/tFR2uvK) Discord in the #simpermut-autosimc Channel to ask about specific stuff.


## How does it work ?
You must have python (ideally >3.6) installed on you computer for this to work.
- Check your environment-variables (python.exe should be in "path"). If not, edit absolute path into launch.bat
- Download the project and extract it.
- Open input.txt and enter parameters depending on your character (see below for more informations). Save and close.
- Edit settings.py for additional parameters (e.g. #legendaries, iterations, threads, fightstyle etc.)
- Launch launch.bat (see below for more parameters)
- The .simc file is generated and ready to be used with Simc.
- If you are using Simc GUI, open the .simc file with notepad and copy/paste the text in simc
- You can use the -sim-option to simulate it without using the Simcraft-Gui

## Input.txt
[This might not work fully with the current [-sim]-option]

You have to fill variables as it is on SimulationCraft.

If you want to add rotations, stance or others advanced SimulationCraft feature, add them with the "other=" field :
Example :

    other=initial_chi=4 for Monks
You MUST add "\n" between each lines to make a line break.
Example :

    other=initial_chi=4\nactions+=/stance,choose=fierce_tiger

For the gear part, simply copy the gear part of the SimulationCraft addon. If you want to test different gear, add the simulationcraft string of the gear separated with a pipe ( the caracter " | ") 
Example : 

    neck=,id=130234,enchant_id=5890,bonus_id=1762/689/600/670,gem_id=130220|,id=134529,enchant_id=5890,bonus_id=3413/1808/1507/3336,gem_id=130220

You can also use SimPermut to generate the string directly with the gear you have equipped and in your bag (See below).

## Launch.bat
Command :

    python main.py -i inputFile -o outputFile -l [Leg_list [Min_leg]:[Max_Leg]] [-quiet] [-sim [stage1|stage2|stage3]]

What can be changed (command prefix are case sensitive):
- -i inputFile : This is the input file. You can have multiple settings.ini files in case you have multiple char/spec/want to test different things. just type the settings file. (ie : input.txt)
- -o outputFile : this is the output file. As the input file, you can have different output file (ie : out.simc)
- -quiet : Option for disabling Console-output. Generates the outputfile much faster for large permuation-size
- -sim : Enabled automated simulation and ranking for the top 3 dps-gear-combinations. Might take a long time, depending on number of permutations. Edit the simcraft-path in splitter.py to point to your simc-installation. The result.html will be saved in temp_step3.
         There are 2 modes available for calculating the possible huge amount of permutations:
         Static and dynamic mode:
         Static uses a fixed amount of simc-iterations at the cost of quality; default-settings are 100, 1000 and 10000 for each stage.
         Dynamic mode lets you set the target_error-parameter from simc, resulting in a more accurate ranking. Stage 1 can be entered at the beginning in the wizard. Stage 2 is set to target_error=0.4, and 0.1 for the final stage 3.
         (These numbers might be changed in future versions)
         It is now also possible to "resume" at stage1, 2 or 3, if a previous stage has been fully calculated and generated a .result in the equivalent folder. Please use this feature with care.
         (default: -sim stage1)
		 You have to set the simc path in the setttings.py file.
  
After are parameters that I added to help Aethys build SimulationCraft's best legendary combinations for each class easily
- -l Leg_List : List of legendaries to add to the template. Format :

    "leg1/id/bonus/gem/enchant,leg2/id2/bonus2/gem2/enchant2,..."

(seperate each leg with a comma (",") and wrap everything with double quote (" " ")
- Min_leg : Minimum number of legendaries in the permutations. Default : 0
- Max_Leg : Maximum number of legendaries in the permutations. Default : 2

You can change a good number of settings in the settings.py file.

## Analyzer:
Included is Analyzer.py, which uses the standard-simc-profiles for each class to generate a Analysis.json (in profiles-folder), which represents calculation data for each class/spec.
 It is used in the main-program to show the approximate calculation times, therefore it is only needed to be recalculated at major WoW- and Simcraft-updates, e.g. 7.2.5

 Modules needed: marshmallow (pip install marshmallow) for generating json-files easier

## SimPermut complementarity
SimPermut ([On GitHub](https://github.com/Kutikuti/SimPermut)) allows you to extract a settings.ini file to directly calculate the profiles with the items you have in your bags.
Just copy the text you get in SimPermut and paste it in your input.txt file (erase what was already in it) and launch the script as described above.

## Known issues and developement plan
- Better management of command line
- Bugfixing and expanding simulation-options

[-Relic comparison]


## Credits
Aethys

Kutikuti (SimPermut integration)

Bickus (All the fancy things)


