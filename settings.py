import multiprocessing


class settings():
    # ----------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>  I M P O R T A N T ! ! ! ! ! <<<<<<<<<<<<<<<<<<<<<<
    # ----------------------------------------------------------------------
    # Path to your simc.exe (or binary on linux/mac) if you enable the simulation-part.
    # Don´t point to the gui-executable. If a window with buttons and tabs opens, you chose the wrong executable!
    # Don´t forget to >>>>INCLUDE DOUBLE-BACKSLASH<<<< for subfolders, like in the example.
    simc_path = 'D:/dev/git/AutoSimC/auto_download/simc-730-03-win64/simc.exe'
    # or enable auto_download_simc of latest nightly, need 7z command line utility in path to unzip
    auto_download_simc = True

    # ----------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>  I M P O R T A N T ! ! ! ! ! <<<<<<<<<<<<<<<<<<<<<<
    # ----------------------------------------------------------------------

    # standard-input
    default_inputFileName = "input.txt"
    # standard-output
    default_outputFileName = "out.simc"

    logFileName = "logs.txt"
    errorFileName = "error.txt"

    # set minimal amount of legendaries to be simulated
    # if min=max=2, it never simulates combinations with fewer legendaries, therefore rapidly decreasing the total
    # amount of possible combinations
    # beware: if you do not include at least leg_min legendaries into your simpermut-output, it might produce errors
    # you can still override these settings via command-line (-l "" 2:2), as described in the readme
    # enter max=3 only if you want to include the new Amanthul-Trinket
    default_leg_min = 2
    default_leg_max = 3

    # ----------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>  I M P O R T A N T ! ! ! ! ! <<<<<<<<<<<<<<<<<<<<<<
    # ----------------------------------------------------------------------
    # set the amount of tier-items you want to include in your output
    # this reduces the number of permutations generated if you know what you want to sim
    # if you have no clue which items do what (= sim every combination), set all txx_min to 0 and txx_max to 6
    # common errors are setting min=max=0 for a particular tier, which result in no tier-sets being equipped at all
    default_equip_t19_min = 0
    default_equip_t19_max = 6
    default_equip_t20_min = 4
    default_equip_t20_max = 6
    default_equip_t21_min = 0
    default_equip_t21_max = 6

    # quiet_mode for faster output; console is very slow
    # default 0; 1 for reduced console-output
    b_quiet = 0

    # split after n profiles. 50 seems to be a good number for this,
    # it takes around 10-20s each, depending on simulation-parameters
    # Splitting into too small sets will generate a lot of temporary files on disk and slow things down
    # Too large split size will require more memory for SimulationCraft and slows down the simulation.
    splitting_size = 50

    # Default sim start stage. Valid options: "permutate_only", "all", "stage1", "stage2", "stage3" 
    default_sim_start_stage = "all"

    # Inside this folder files&folders will be created during calculation
    temporary_folder_basepath = "tmp"

    # Number of stages to simulate
    # It is recommended to have at least 2, better 3 stages to benefit from
    # increasing accuracy and filtering number of profiles down on each stage.
    # The optimal settings depends on the number of profiles you have on your input side.
    # Default: 3
    # Please not that you must extend 'default_iterations', 'default_target_error' and 'default_top_n'
    # If you want to use this with a value > 3
    num_stages = 3

    # Automatic delete of the temp folders
    delete_temp_default = False

    # set to False if you want to keep intermediate files
    # moves the final .html-result into the specified subfolder before deletion
    # the resulting html will be renamed to: <Timestamp - best.html>
    clean_up = True

    result_subfolder = "results"

    # for static mode, default iterations per stage
    # by default this is 100 for stage1, 1000 for stage2, and so on.
    # default_iterations = {1: 100,
    #                       2: 1000,
    #                       3: 10000,}
    default_iterations = {i: 10**(i+1) for i in range(1, num_stages+1)}

    # for dynamic mode
    # pls override this, especially stage2, if you think it is too erroneus, it depends on the chosen class/spec
    # the top100 will be simulated in stage2 and top3 in stage 3; stage1 can be chosen dynamically
    # beware: if you simulate the first stage with a very low target_error (<0.2), stage2 and stage 3 might become
    # obsolete this case might not get fully supported because of the indivduality of these problems
    #
    # If you leave a stage empty, you will be asked to input a target_error during runtime
    # Remove all entries if you want to be asked at each stage
    default_target_error = {1: 1.0,
                            2: 0.2,
                            3: 0.05,
                            4: 0.05}

    # alternate method to determine the "best" profiles when using target_error-method
    # it does not choose fixed top n for each stage
    # instead it uses the following algorithm:
    # 1. create the list of profile-dps as usual, descending order
    # 2. if iterates the list and removes all profiles which do not fulfil (topdps-target_error) > profiledps
    # e.g. target_error chosen in stage1 = 0.5, topdps = 1.000.000 -> it includes all profiles for stage2
    # with dps > 995.000
    # 3. use the same procedure for stage3
    # set this to True|False if you want to use this method
    # Non-alternate grabbing method is no longer recommended, since it will lead to unneeded calculations and
    # cannot give you a statistically correct selection of the "equally best" profiles by only looking at the
    # dps without checking statistical variation.
    default_use_alternate_grabbing_method = True

    # Number of profiles to grab with normal method, in reverse order
    # This means 1: represents the last stage, while 2: is for the next_to_last stage, etc.
    # default_top_n = {1: 1,
    #                  2: 100,
    #                  3: 1000}
    default_top_n = {-i: 100**(i-1) for i in range(1, num_stages)}

    # Error Rate Multiplier / Confidence Range
    # change this to widen/narrow the interval of profiles taken into account for the next stage
    # use 1.96 for 95% confidence or 2.58 for 99% confidence
    default_error_rate_multiplier = 1.96

    # Patchwerk, LightMovement, HeavyMovement, HelterSkelter, HecticAddCleave, Ultraxion, Beastlord, CastingPatchwerk
    # https://github.com/simulationcraft/simc/wiki/RaidEvents
    default_fightstyle = "Patchwerk"

    # enter desires priority
    # low, below_normal, normal, above_normal, highest
    simc_priority = "low"

    # number of threads for simc. Default uses as many cores as available on your system.
    # https://github.com/simulationcraft/simc/wiki/Options#multithreading
    simc_threads = max(int(multiprocessing.cpu_count()), 1)
    # True|False
    simc_scale_factors_stage3 = True

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

    # console output tends to get spammy with mutliple instances running at once; this enables/disables this behaviour
    # keep in mind that, if enabled, there will be NO output at all, which may be confusing
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
    # enter the number of the number you would enter when being presented the target_error_table
    # (run once with skip_questions=False to look it up if you dont know)
    auto_dynamic_stage1_target_error_table = 8
    # beware: in the current state it is not detectable in which stage it crashed respectively autosimc was restarted
    # if you are unsure, try a higher/better amount to not skew the results too much
    # resim for static mode gets its values from variables above (default_iterations_stage1,..)
    # because target_error for dynamic mode has to be entered manually normally, you can set it here
    # most probably you will enter here the value represented by auto_dynamic_stage1_target_error_table
    auto_dynamic_stage1_target_error_value = 0.9

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
