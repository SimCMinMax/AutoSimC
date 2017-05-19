AutoSimC
========

Python script to create multiple profiles for SimulationCraft to find Best-in-Slot and best enchants/gems/talents combination.

Don't hesitate to go on the [SimcMinMax](https://discordapp.com/invite/tFR2uvK) Discord to ask about specific stuff.


## How does it work ?
You must have python installed on you computer for this to work.
- Download the project and extract it.
- Open Settings.ini and enter parameters dependings on your character (Use a real editor like Notepad++)(see below for more informations). Save and close. 
- Launch launch.bat (see below for more parameters)
- The .simc file is generated and ready to be used with Simc.
- If you are using Simc GUI, open the .simc file with notepad and copy/paste the text in simc

## Settings.ini
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

You can also use SimPermut to generate the string directly with the gear you have equiped and in you bag (See below).

## Launch.bat
Command :

    python main.py -i inputFile -o outputFile -l [Leg_list [Min_leg]:[Max_Leg]]

What can be changed (command prefix are case sensistive):
- -i inputFile : This is the input file. You can have multiple settings.ini files in case you have multiple char/spec/want to test different things. just type the settings file. (ie : settings.ini)
- -o outputFile : this is the output file. As the input file, you can have different output file (ie : out.simc)
  
  
After are parameters that I added to help Aethys build SimulationCraft's best legendary combinations for each class easily
- -l Leg_List : List of legendaries to add to the template. Format :

    "leg1/id/bonus/gem/enchant,leg2/id2/bonus2/gem2/enchant2,..."

(seperate each leg with a coma (",") and wrap everything with double quote (" " ")
- Min_leg : Minimum number of lengendaries in the permutations. Default : 0
- Max_Leg : Maximum number of lengendaries in the permutations. Default : 2

## SimPermut complementarity
SimPermut ([On GitHub](https://github.com/Kutikuti/SimPermut)) allows you to extract a settings.ini file to directly calculate the profiles with the items you have in your bags.
Just copy the text you get in SimPermut and paste it in you settings.ini file (erase what was already in it) and launch the script as you described above.

## Known issues and developement plan
- Better management of command line  
- Reduce number of copies with ring/trinket inversion

[-Relic comparison]


## Credits
Aethys

Kutikuti (SimPermut integration)

[Quichons guild](http://www.quichons.fr/) from EU-Elune (fr).
