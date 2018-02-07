import multiprocessing


class settings():
    # Path to your SimulationCraft command line binary (simc.exe on Windows, or simc on linux/mac).
    # If you enable the simulation-part, you need to either set simc_path, or enable auto_download on Windows.
    # Don´t point to the gui-executable. If a window with buttons and tabs opens, you chose the wrong executable!
    # Either use forward slashes, or >>>>SINGLE-BACKSLASH<<<< for subfolders. Do not remove the leading r'
    #simc_path = 'E:\\Simulationcraft(x64)\\735-01\\simc.exe'
    simc_path = r'simc.exe'

    # On Windows, AutoSimCor can automatically download the latest nightly version of SimulationCraft for you.
    # You need 7z command line utility in path to unzip for this to work.
    auto_download_simc = False

    # standard-input
    default_inputFileName = "input.txt"

    # standard-output
    default_outputFileName = "out.simc"

    # standard log file
    logFileName = "logs.txt"

    # standard error file
    errorFileName = "error.txt"

    # Minimal/Maximal amount of legendaries for a profile combination to be valid.
    # If min=max=2, it never simulates combinations with fewer legendaries, therefore rapidly decreasing the total
    # amount of valid combinations
    # You can override these settings via command-line (-min_leg and -max_leg), as described in the Readme.
    # Enter max=3 only if you want to include the new Amanthul-Trinket
    default_leg_min = 2
    default_leg_max = 3

    # set the amount of tier-items you want to include in your output
    # this reduces the number of permutations generated if you know what you want to sim
    # if you have no clue which items do what (= sim every combination), set all txx_min to 0 and txx_max to 6
    # common errors are setting min=max=0 for a particular tier, which result in no tier-sets being equipped at all
    default_equip_t19_min = 0
    default_equip_t19_max = 6
    default_equip_t20_min = 0
    default_equip_t20_max = 6
    default_equip_t21_min = 0
    default_equip_t21_max = 6

    # quiet_mode for faster output; console is very slow
    # default 0; 1 for reduced console-output
    # No longer used for main.py
    b_quiet = 0

    # Number of profiles to split simulation work into.
    # This means that each SimulationCraft instance will simulate at most this many profiles.
    #
    # 50 seems to be a good number for this, it takes around 10-20s each and a moderate amount of memory,
    # depending on simulation-parameters
    # Splitting into too small sets will generate a lot of temporary files on disk and slow things down
    # Too large split size will require large amounts of memory for SimulationCraft and slow down the simulation.
    splitting_size = 50

    # Default sim start stage. Valid options: "permutate_only", "all", "stage1", "stage2", "stage3", ...
    # 'permutate_only' will only generate profile combinations.
    # 'all' generates profiles & starts simulation process at stage1.
    # 'stageN' restarts simulation process at stage N.
    default_sim_start_stage = "all"

    # Folder in which temporary files for simulation are created.
    temporary_folder_basepath = "tmp"

    # Number of stages to simulate
    # It is recommended to have at least 2, better 3 stages to benefit from
    # increasing accuracy and filtering number of profiles down on each stage.
    # The optimal settings depends on the number of profiles you have on your input side.
    # Default: 3
    # Please not that you must extend 'default_iterations', 'default_target_error' and 'default_top_n'
    # If you want to use this with a value > 3 with skip_questions.
    # This value can also be change through command line argument --stages.
    num_stages = 3

    # Automatic delete of the temp folders
    delete_temp_default = True

    # set to False if you want to keep intermediate files
    # moves the final .html-result into the specified subfolder before deletion
    # the resulting html will be renamed to: <Timestamp - best.html>
    clean_up = True

    result_subfolder = "查看结果"

    # For static mode, default iterations per stage
    # By default this is 100 for stage1, 1000 for stage2, and so on.
    # If you do not specify a stage, you will be asked during simulation if skip_questions is False
    default_iterations = {1: 100,
                          2: 1000,
                          3: 10000}

    # For dynamic mode, default target_error per stage
    # Please override this, especially stage2, if you think it is too erroneus, it depends on the chosen class/spec
    # Beware: if you simulate the first stage with a very low target_error (<0.2), stage2 and stage 3 might become
    # obsolete. This case might not get fully supported because of the indivduality of these problems.
    #
    # Please note that you should not just decrease the target_error indefinitely. While this minimises the statistical
    # error, at some point errors in the modelling in SimulationCraft will mean that you should just accept that two
    # profiles are 'about equal'.
    #
    # If you leave a stage empty, you will be asked to input a target_error during runtime
    # Remove all entries if you want to be asked at each stage
    default_target_error = {1: 1.0,
                            2: 0.2,
                            3: 0.05}

    # Profile grabbing method to determine the "best" profiles when going from stage to stage.
    # There are 2 modes available:
    # 1. 'target_error':
    #     Select all profiles which have statistically the "best" DPS. This means that a variable amount
    #     of profiles get selected depending on the statistical error of the simulation, which depends on the number
    #     of iterations or target_error used.
    #     This also means you need to tweak iterations/target_error setting to get a suitable number of profiles for
    #     each stage.
    # 2. 'top_n':
    #     The profiles are sorted by their DPS, and the top n profiles are selected for the next stage.
    #     The numer of profiles selected, 'n', is specified in settings.default_top_n
    #
    # 'top_n' grabbing method is no longer recommended, since it will lead to unneeded calculations and
    # cannot give you a statistically correct selection of the "equally best" profiles by only looking at the
    # dps without checking statistical variation.
    default_grabbing_method = "target_error"

    # Number of profiles to grab with method 'top_n', in reverse order
    # This means -1: represents the last stage, while -2: is for the next_to_last stage, etc.
    default_top_n = {-1: 1,
                     -2: 100,
                     -3: 1000,
                     -4: 10000}

    # Error Rate Multiplier / Confidence Range
    # change this to widen/narrow the interval of profiles taken into account for the next stage
    # use 1.96 for 95% confidence or 2.58 for 99% confidence
    default_error_rate_multiplier = 1.96

    # Patchwerk, LightMovement, HeavyMovement, HelterSkelter, HecticAddCleave, Ultraxion, Beastlord, CastingPatchwerk
    # https://github.com/simulationcraft/simc/wiki/RaidEvents
    # The fighttypes are stored in fight_types.json
    # You can specify your own fights there by simply extending the list with your own
    # If you set choose_fightstyle to True, a menu pops up before simulation-begin where you can choose the fight to
    # simulate.
    # If set it to False, the entry you declare in the json, e.g. "name":"Default_Patchwerk", has to match default_fightstyle
    file_fightstyle = "fight_types.json"
    choose_fightstyle = False
    default_fightstyle = "Default_Patchwerk"

    # SimulationCraft process priority.
    # This can make your system more/less responsive. We recommend leaving this at 'low'.
    # low, below_normal, normal, above_normal, highest
    simc_priority = "low"

    # number of threads for simc. Default uses as many cores as available on your system.
    # https://github.com/simulationcraft/simc/wiki/Options#multithreading
    simc_threads = max(int(multiprocessing.cpu_count()), 1)

    # Calculate scale factors for the last stage.
    simc_scale_factors_last_stage = 0

    # Should ptr mode be used for SimC
    simc_ptr = False

    # [[deprecated]] enable_talent_permutation
    # Use talent character 0 in your input file to permutate a specific talent row

    # if simc crashes, try to set this variable to "True"; it will set threads=1 and single_actor_batch=0
    # this might also output slightly different results because of single_actor_batch_now simming the input as whole
    # raid instead of single profiles
    simc_safe_mode = False

    # you want this to be set to 1 most of the time; it is used if you want to simulate a whole raid instead of
    # single profiles,
    simc_single_actor_batch = 1

    # additional input you might want to sim according to
    # https://github.com/simulationcraft/simc/wiki/TextualConfigurationInterface
    # the file must be present in the autosimc-folder
    additional_input_file = "additional_input.txt"

    # For Analysis.py
    # set to "nul" if you are simulating healer or tanks
    analyzer_path = "profiles"
    analyzer_filename = "Analysis.json"

    # enables multiple instances of simc if > 1, drastically speeding up simulation.
    # how many instances should run simultaneously
    # if you have e.g. a AMD Ryzen Threadripper (16 Cores, 32 Threads), you should use Cores-1 = 15 number of instances
    # otherwise system gets very laggy as no cores are spare for os-routines
    # Default uses as many cores as available on your system - 1
    number_of_instances = max(int(multiprocessing.cpu_count() - 1), 1)

    # SimulationCraft console output tends to get spammy with mutliple instances running at once;
    # this enables/disables this behaviour
    # keep in mind that, if enabled, there will be NO output at all, which may be confusing
    # Setting this option to False might give you extra information to debug simulation problems.
    multi_sim_disable_console_output = True

    # some tests showed that multisimming is faster with many instances, each with 1 thread
    # you can change this behaviour by modifying this variable
    # number_of_instances > 1, it is recommended to leave this option at 1
    number_of_threads = 1

    # skip interactive user input questions, allowing for full-stage simulation without interruption
    # e.g. "Do you want to resim (yes-no)" will be skipped and automatically started
    # ----------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>  I M P O R T A N T ! ! ! ! ! <<<<<<<<<<<<<<<<<<<<<<
    # ----------------------------------------------------------------------
    # ALL OPTIONS BELOW THIS VARIABLE ARE AFFECTED BY THIS SWITCH!!!
    #               YOU HAVE TO KNOW WHAT YOU DO!
    # ----------------------------------------------------------------------
    skip_questions = False

    # automation of dialogs
    # 1 or 2
    auto_choose_static_or_dynamic = 2

    # ----------------------------------------------------------------------
    #       ALL OPTIONS BELOW THIS ARE USED FOR THE PROFILE GENERATOR
    #                   THEY DON'T IMPACT AUTOSIMC
    # ----------------------------------------------------------------------
    # Profile generator settings
    # Tier to generate
    tier = 21
    # Apply the stat filter to the tier items. If False, all tier items will be added
    apply_stat_filter_to_tier = False
    # filter type (1 : all filter stats have to be present in the item, 2 : one of the stat has to be present)
    filter_type = 2
    # Profile used for the profile bas (talents, artifact, ...).
    # If Empty, it will use the one from autosimc (Use double backslash, like simc path)
    default_profile_path = ".\\profiles"
    # Allow the check of previous tier if selected tier is missing for the spec
    check_previous_tier = True
    minimum_tier_to_check = 20