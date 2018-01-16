AutoSimC [![Build Status](https://travis-ci.org/SimCMinMax/AutoSimC.svg?branch=master)](https://travis-ci.org/SimCMinMax/AutoSimC)
========

Python script to create multiple profiles for SimulationCraft to find Best-in-Slot and best enchants/gems/talents combinations.

Don't hesitate to go on the [SimcMinMax](https://discordapp.com/invite/tFR2uvK) Discord in the #simpermut-autosimc Channel to ask about specific stuff.


## How does it work ?
AutoSimC works in two parts:
1. Generating Permutations: Given a input.txt file and certain settings, an output .simc file is generated containing all possible permutations specified, filtered down to "valid profiles" fullfilling certain requirements. This output file can then be run with SimulationCraft.
2. Simulating the generated profiles in a multi-stage process: To narrow the large amount of generated profiles into a small set of best performing profiles, a multi-stage simulation process is performed, in which each stage simulates the given profiles with increased accuracy to narrow the number of profiles in each stage, resulting in only a handful of final profiles with the best DPS.

## Quick setup
Python (>=3.4) is required for this to work.
- You can download python at https://www.python.org/downloads/. During installation, select *Add Python 3.x to PATH*, so that python gets automatically added to your PATH environment variable.
- Download the project and extract it.
- Open [input.txt](#inputtxt) and enter parameters depending on your character. Make sure your text editor encodes input.txt as UTF-8.
- Either install 7zip for auto download of nightly SimulationCraft, or edit settings.py to set auto_download_simc=False and set the simc_path.
- Edit [settings.py](settingspy) for additional parameters (e.g. #legendaries, iterations, threads, fightstyle etc.)
- Run launch.bat or run 'python main.py' directly. See [below](#command-line-interface) for detailed options.
- You can use the -sim option to simulate directly with AutoSimC. Or you can feed to generated output .simc file into SimulationCraft yourself.
- You can also follow this how-to set it up [https://goo.gl/5d7BAM].

## Command Line Interface
    python main.py [-h] [-i INPUTFILE] [-o OUTPUTFILE]
						[-sim {permutate_only,all,stage1,stage2,stage3,stage4,stage5}]
						[--stages STAGES] [-gems [GEMS [GEMS ...]]] [-l LEGENDARIES]
						[-min_leg LEGENDARY_MIN] [-max_leg LEGENDARY_MAX]
						[--unique_jewelry UNIQUE_JEWELRY] [--debug] [-quiet]
						[--version]

		Python script to create multiple profiles for SimulationCraft to find Best-in-
		Slot and best enchants/gems/talents combinations.

		optional arguments:
		  -h, --help            show this help message and exit
		  -i INPUTFILE, --inputfile INPUTFILE
								Inputfile describing the permutation of SimC profiles
								to generate. See README for more details. (default:
								input.txt)
		  -o OUTPUTFILE, --outputfile OUTPUTFILE
								Output file containing the generated profiles used for
								the simulation. (default: out.simc)
		  -sim {permutate_only,all,stage1,stage2,stage3,stage4,stage5}
								Enables automated simulation and ranking for the top 3
								dps-gear-combinations. Might take a long time,
								depending on number of permutations. Edit the
								simcraft-path in settings.py to point to your simc-
								installation. The result.html will be saved in
								results-subfolder.There are 2 modes available for
								calculating the possible huge amount of permutations:
								Static and dynamic mode:* Static uses a fixed amount
								of simc-iterations at the cost of quality; default-
								settings are 100, 1000 and 10000 for each stage.*
								Dynamic mode lets you set the target_error-parameter
								from simc, resulting in a more accurate ranking. Stage
								1 can be entered at the beginning in the wizard. Stage
								2 is set to target_error=0.2, and 0.05 for the final
								stage 3.(These numbers might be changed in future
								versions) You have to set the simc path in the
								settings.py file.
								- Resuming: It is also possible to resume at a stage,
								e.g. if simc.exe crashed during	stage1, by launching
								with the parameter -sim stage1 (or stage2/3).
								- Parallel Processing: By default multiple simc-
								instances are launched for stage1 and 2, which is a
								major speedup on modern multicore-cpus like AMD Ryzen.
								If you encounter problems or instabilities, edit
								settings.py and change the corresponding parameters
								or even disable it.	(default: ['all'])
		  --stages STAGES       Number of stages to simulate. (default: 3)
		  -gems [GEMS [GEMS ...]], --gems [GEMS [GEMS ...]]
								Enables permutation of gem-combinations in your gear.
								With e.g. gems crit,haste,int you can add all
								combinations of the corresponding gems (epic gems:
								200, rare: 150, uncommon greens are not supported) in
								addition to the ones you have currently equipped.
								Valid gems: ['150haste', '200haste', 'haste',
								'150crit', '200crit', 'crit', '150vers', '200vers',
								'vers', '150mast', '200mast', 'mast', '200str', 'str',
								'200agi', 'agi', '200int', 'int']- Example: You have
								equipped 1 int and 2 mastery-gems. If you enter <-gems
								"crit,haste,int"> (without <>) into the commandline,
								the permutation process uses the single int- and
								mastery-gem-combination you have currrently equipped
								and adds ALL combinations from the ones in the
								commandline, therefore mastery would be excluded.
								However, adding mastery to the commandline reenables
								that.
								- Gems have to fulfil the following syntax in
								your profile: gem_id=123456[[/234567]/345678]
								Simpermut usually creates this for you.
								- WARNING: If you have many items with sockets and/or
								use a vast gem-combination-setup as command, the number
								of combinations will go through the roof VERY quickly.
								Please be cautious when enabling this.- additonally
								you can specify a empty list of gems, which will
								permutate the existing gemsin your input gear.
								(default: None)
		  -l LEGENDARIES, --legendaries LEGENDARIES
								List of legendaries to add to the template. Format: "l
								eg1/id/bonus/gem/enchant,leg2/id2/bonus2/gem2/enchant2
								,..." (default: None)
		  -min_leg LEGENDARY_MIN, --legendary_min LEGENDARY_MIN
								Minimum number of legendaries in the permutations.
								(default: 2)
		  -max_leg LEGENDARY_MAX, --legendary_max LEGENDARY_MAX
								Maximum number of legendaries in the permutations.
								(default: 3)
		  --unique_jewelry UNIQUE_JEWELRY
								Assume ring and trinkets are unique-equipped, and only
								a single item id can be equipped. (default: true)
		  --debug               Write debug information to log file. (default: False)
		  -quiet                Run quietly. /!\ Not implemented yet (default: False)
		  --version             show program's version number and exit

		Don't hesitate to go on the SimcMinMax Discord
		(https://discordapp.com/invite/tFR2uvK) in the #simpermut-autosimc Channel to
		ask about specific stuff.



## Input.txt
Follow the example that is downloaded and modify it with your own character.

For the gear part, simply copy the gear part of the SimulationCraft addon. If you want to test different gear, add the simulationcraft string of the gear separated with a pipe ( the caracter " | ").
Example : 

    neck=,id=130234,enchant_id=5890,bonus_id=1762/689/600/670,gem_id=130220|,id=134529,enchant_id=5890,bonus_id=3413/1808/1507/3336,gem_id=130220

To specify Tier set and item names, use the following syntax:

    neck=T21--chain_of_the_unmaker,id=152283,enchant_id=5890
    
To specify a legendary, use the following syntax:

    waist=L--Mangazas_Madness,id=132864,bonus_id=1811/3630
    
(item name is not necessary)  

You can also use [SimPermut](#simpermut-complementarity) to generate the string directly with the gear you have equipped and in your bag.

If you want to add rotations, stance or others advanced SimulationCraft feature, add them with the "other=" field :
Example :

    other=initial_chi=4 for Monks
You MUST add "\n" between each lines to make a line break.
Example :

    other=initial_chi=4\nactions+=/stance,choose=fierce_tiger

For talent permutation, just replace the talent row your want to permutate (talents 1, 2 and 3) with a 0 in your talent= string.

## settings.py
You can/have to finetune your settings in the settings.py file:
- set min/max amount of tier-items and legendaries
- default number of iterations or target_error for each stage
- change default for type of fight (patchwerk, LightMovement etc.)
- and several more

For developers/power users:
- You can add a copy of settings.py named settings_local.py to provide overrides for you local settings. 
  Since this file is not part of AutoSimc source, it will not be overridden/commited when pulling/pushing to
  the AutoSimC remote repository.
  For now, please ensure that your local copy stays in sync with settings.py whenever new options are added/renamed.

## Analyzer:
Included is Analyzer.py, which uses the standard-simc-profiles for each class to generate a Analysis.json (in profiles-folder), which represents calculation data for each class/spec.
 It is used in the main-program to show the approximate calculation times, therefore it is only needed to be recalculated at major WoW- and Simcraft-updates, e.g. 7.2.5, and if you want to sim your tank- or healspec. Edit the Analysis.py accordingly.

 Modules needed: marshmallow (pip install marshmallow) for generating json-files easier
 
## Fight-Type Selector:
In fight_types.json you can define your personal fight_types.
The standard simc-profiles are already included, it is advised not to touch these.

If you want to expand them, e.g. simulate two Patchwerks in cleave-range, simply add a block with the commands you would normally add to additional_input.txt. Use the syntax given in the two examples.

*WARNING*: Currently it is therefore NOT advised to touch additional_input.txt AT ALL. For now leave it empty and create a new profile with your custom commands.

## SimPermut complementarity
SimPermut ([On GitHub](https://github.com/Kutikuti/SimPermut)) allows you to extract a profile-set file to directly calculate the profiles with the items you have in your bags.
Just copy the text you get in SimPermut and paste it in your input.txt file (erase what was already in it) and launch the script as described above.

## Known issues and developement plan
- Bugfixing and expanding simulation-options

## Frequently Asked Questions
1. I get an error message *RuntimeError: AutoSimC could not decode your input file 'input.txt' with encoding 'utf-8'.*

   This means that the textual content you stored in 'input.txt' is not encoded with 'utf-8', which AutoSimC expects for this file.
  Your text editor with which you edited 'input.txt' chose a incompatible encoding when saving the file.
  To resolve this issue, tell your text editor to save the file with a 'utf-8' encoding. Alternatively, you can remove any special, non-ASCII character from the file to circumvent the problem, since ASCII is a subset of most encodings.
1. I get an error message *ValueError: No valid profile combinations found. Please check the 'Invalid profile statistics' output and adjust your input.txt and settings.py.*

   This means that when AutoSimC generated all possible combinations and filtered them according to the criterias set up in settings.py, 0 valid profiles have been generated. Usually, this is because that your profile does not match the filtering criteria in settings.py about min_legendaries, max_legendaries, tier_min and tier_max number of items required.
  To resolve this issue, check the console/log output line starting with *Invalid profile statistics* to see a list of reasons and their percentage for rejecting the generated profiles. It should then be easy to adjust your profile or settings.py to get some valid profiles.

1. How can I simulate multiple enemy targets?

   Basic: Check 'additional_input.txt' to provide additional simulation options. You can adust the *desired_targets* option.
   Advanced: You can edit fight_types.json to generate your own database of fights. If using this option, leave additional_input.txt empty as it gets overwritten during the process.
  
1. Simulation crashed/stoped at stage x. How can I restart AutoSimC at stage x, without redoing all the previous work?

   Start AutoSimC with the argument *-sim stagex*. If you use launch.bat, edit it and adjust the -sim argument in there.
   This will resume AutoSimC at stage x, assuming all previous results are ok and you did not clean up the temp folder.
   
1. I get an error message *ModuleNotFoundError: No module named 'settings'*

   That means you have no settings.py file. Rename settings.template.py to settings.py.
   
1. How can I get back the target error selection dialog for each stage?

   In settings.py, remove the default_target_error for a given stage and you will be prompted for a target error selection for that stage, assuming skip_questions is False.
   
  

## Changelog

- 7.3.2a:
  - Autosimc seems to be stable, therefore bumping version to match compatibility with the current WoW-Patch.
  - Added additional functionality: Choose fightstyle dynamically before simulation starts. Edit fight_types.json accordingly.


## Credits
Aethys

Kutikuti (SimPermut integration)

Bickus (All the fancy things)

Aadder (How-To)

Serge (Lot of rework)
