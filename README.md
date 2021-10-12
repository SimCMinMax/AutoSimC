AutoSimC [![Build Status](https://travis-ci.org/SimCMinMax/AutoSimC.svg?branch=master)](https://travis-ci.org/SimCMinMax/AutoSimC)
========

Python script to create multiple profiles for SimulationCraft to find Best-in-Slot and best enchants/gems/talents combinations.

Don't hesitate to go on the [SimcMinMax](https://discordapp.com/invite/tFR2uvK) Discord in the #simpermut-autosimc Channel to ask about specific stuff.

## How does it work ?
AutoSimC works in two parts:
1. Generating Permutations: Given a input.txt file and certain settings, an output .simc file is generated containing all possible permutations specified, filtered down to "valid profiles" fullfilling certain requirements. This output file can then be run with SimulationCraft.
2. Simulating the generated profiles in a multi-stage process: To narrow the large amount of generated profiles into a small set of best performing profiles, a multi-stage simulation process is performed, in which each stage simulates the given profiles with increased accuracy to narrow the number of profiles in each stage, resulting in only a handful of final profiles with the best DPS.

## Quick setup
Python (>=3.5) is required for this to work.
- You can download python at https://www.python.org/downloads/. During installation, select *Add Python 3.x to PATH*, so that python gets automatically added to your PATH environment variable.
- Download the project and extract it.
- Open [input.txt](#inputtxt) and enter parameters depending on your character. Make sure your text editor encodes input.txt as UTF-8.
- Either install 7zip for auto download of nightly SimulationCraft (Windows only), or edit settings.py to set auto_download_simc=False and set the simc_path.
- If using **Ubuntu**, read [here](#ubuntu) to use the auto-download script.
- Edit [settings.py](settingspy) for additional parameters (e.g. #legendaries, iterations, threads, fightstyle etc.)
- Run launch.bat or run 'python main.py' directly. See [below](#command-line-interface) for detailed options.
- You can use the -sim option to simulate directly with AutoSimC. Or you can feed to generated output .simc file into SimulationCraft yourself.
- You can also follow this how-to set it up [https://goo.gl/5d7BAM].

## Command Line Interface
    python main.py [-h] [-i INPUTFILE] [-o OUTPUTFILE]
						[-sim {permutate_only,all,stage1,stage2,stage3,stage4,stage5}]
						[--stages STAGES] [-gems [GEMS [GEMS ...]]]
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
								40, rare: 40, green: 30) in
								addition to the ones you have currently equipped.
								Valid gems: ['30haste', '40haste', 'haste',
								'30crit', '40crit', 'crit', '30vers', '40vers',
								'vers', '30mast', '40mast', 'mast', '40str', 'str',
								'40agi', 'agi', '40int', 'int']- Example: You have
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
								- WARNING: If you have many items with sockets and/or
								use a vast gem-combination-setup as command, the number
								of combinations will go through the roof VERY quickly.
								Please be cautious when enabling this.- additonally
								you can specify a empty list of gems, which will
								permutate the existing gemsin your input gear.
								(default: None)
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

To specify item names, use the following syntax:

    neck=chain_of_the_unmaker,id=152283,enchant_id=5890

(item name is not necessary)

If you want to add rotations, stance or others advanced SimulationCraft feature, add them with the "other=" field :
Example :

    other=initial_chi=4 for Monks
You MUST add "\n" between each lines to make a line break.
Example :

    other=initial_chi=4\nactions+=/stance,choose=fierce_tiger

For talent permutation, just replace the talent row your want to permutate (talents 1, 2 and 3) with a 0 in your talent= string.

## settings.py
You can/have to finetune your settings in the settings.py file:
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
In fight_types.json you can define your personal fight_types. In settings.py you must select the desired fight style in the option *default_fightstyle*.
The standard simc-profiles are already included, it is advised not to touch these.

If you want to expand them, e.g. simulate two Patchwerks in cleave-range, simply add a block with the commands you would normally add to additional_input.txt. Use the syntax given in the two examples.

If you want to expand already existing fights, e.g. Beastlord: Create a new Profile, remove the "command"-line and put into "line1":"fight_style=Beastlord". All lines after that can now contain your overrides etc.

*WARNING*: Currently it is therefore NOT advised to touch additional_input.txt AT ALL. For now leave it empty and create a new profile with your custom commands.

## Known issues and developement plan
- Bugfixing and expanding simulation-options

## Ubuntu
- AutoSimC comes with a simple bash script to help you automatically download and install the latest version of SimC.
- The script will also automatically run AutoSimC after it installs SimC.
- Simply run `sh launch-ubuntu.sh` and it will guide you through a few prompts for installation.
- Optionally:  You can pass in your own 'input.txt' (named whatever you want) to use in the script. (`sh launch-ubuntu.sh my-class-input.txt`)
- This will create a `settings_local.py` file in your AutoSimC folder which will have the correct 'path' to your simc executable.  Note:  This file is made from a copy of your `settings.py`.  If you install simc again, it will be overwritten by your `setting.py` file.
- If you do not have the required dependencies, you will need to run the script as root or install them yourself (`build-essential` `libssl-dev`)
- The script assumes that your python 3.4 executable is called `python3`.  If this is not the case, please edit to use the correct value in your `PATH`.
- SimulationCraft requires you to compile the source code yourself, This script will do this for you but it may take some time. Run the compilation each time you want to update your executable.
- The script will NOT inform you when its time to update.  Simply check the commit hash in the folder name against the simc repo.

## Frequently Asked Questions
1. I get an error message *RuntimeError: AutoSimC could not decode your input file 'input.txt' with encoding 'utf-8'.*

   This means that the textual content you stored in 'input.txt' is not encoded with 'utf-8', which AutoSimC expects for this file.
  Your text editor with which you edited 'input.txt' chose a incompatible encoding when saving the file.
  To resolve this issue, tell your text editor to save the file with a 'utf-8' encoding. Alternatively, you can remove any special, non-ASCII character from the file to circumvent the problem, since ASCII is a subset of most encodings.
1. I get an error message *ValueError: No valid profile combinations found. Please check the 'Invalid profile statistics' output and adjust your input.txt and settings.py.*

   This means that when AutoSimC generated all possible combinations and filtered them according to the criterias set up in settings.py, 0 valid profiles have been generated. Usually, this is because that your profile does not contain a valid configuration.
  To resolve this issue, check the console/log output line starting with *Invalid profile statistics* to see a list of reasons and their percentage for rejecting the generated profiles. It should then be easy to adjust your profile or settings.py to get some valid profiles.

1. How can I simulate multiple enemy targets?

   See [Fight-Type Selector](#fight-type-selector) for detailed instructions on how to select different fight types, including simulating against multiple enemies.

1. Simulation crashed/stoped at stage x. How can I restart AutoSimC at stage x, without redoing all the previous work?

   Start AutoSimC with the argument *-sim stagex*. If you use launch.bat, edit it and adjust the -sim argument in there.
   This will resume AutoSimC at stage x, assuming all previous results are ok and you did not clean up the temp folder.

1. I get an error message *ModuleNotFoundError: No module named 'settings'*

   That means you have no settings.py file. Rename settings.template.py to settings.py.

1. How can I get back the target error selection dialog for each stage?

   In settings.py, remove the default_target_error for a given stage and you will be prompted for a target error selection for that stage, assuming skip_questions is False.

## Localization

AutoSimC has experimental support for localization/translation using the [gettext](https://docs.python.org/3/library/gettext.html) module. You can improve or extend our translation efforts even as a non-programmer.

- All string to be translated in the source code need to be enclose in \_(). So "Hello World" becomes \_("Hello World").
- All strings marked with \_() are extracted by the pygettext script. Run *update_language_file.py* to update the extracted language file *AutoSimC.pot* with any changes done in the source code.
- To edit & create new translations, we recommend a graphical PO editor, like [Poedit](https://poedit.net/).
- A new translation for a language needs to go in a specific folder following the scheme, eg. for language "de":          ```./locale/de/LC_MESSAGES/AutoSimC.mo
  ./locale/de/LC_MESSAGES/AutoSimC.po```
- To update a existing translation *.po* file from a updated *AutoSimc.pot* file, in [Poedit](https://poedit.net/) select *Catalog -> Update from POT file*.
- In settings.py there is a option *localization_language* to control the language to which AutoSimC is translated. Default is "auto", selecting the language based on your system setting.

## Changelog

- 9.1.0a:
- added basic functionality for Shadowlands

- 8.0.1a:
- removed Simpermut-import, now uses Simulationcraft-Addon [https://wow.curseforge.com/projects/simulationcraft]

- 8.0.1:
- Support for BfA

- 7.3.2a:
  - Autosimc seems to be stable, therefore bumping version to match compatibility with the current WoW-Patch.
  - Added additional functionality: Choose fightstyle dynamically before simulation starts. Edit fight_types.json accordingly.


## Credits
Aethys

Kutikuti (SimPermut integration)

Bickus (All the fancy things)

Aadder (How-To)

Serge (Lot of rework)
