class settings():
    # ----------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>  I M P O R T A N T ! ! ! ! ! <<<<<<<<<<<<<<<<<<<<<<
    # ----------------------------------------------------------------------
    # Path to your simc.exe (or binary on linux/mac) if you enable the simulation-part.
    # Don´t point to the gui-executable. If a window with buttons and tabs opens, you chose the wrong executable!
    # Don´t forget to >>>>INCLUDE DOUBLE-BACKSLASH<<<< for subfolders, like in the example.
    # Lnk to the      >>>> simc.EXE, NOT Simulationcraft.exe <<<<
    simc_path = 'D:\\Programme\\Simcraft\\simc-725-02-win64\\simc.exe'
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
    # beware: if you don´t include at least leg_min legendaries into your simpermut-output, it might produce errors
    # you can still override these settings via command-line (-l "" 2:2), as described in the readme
    default_leg_min = 2
    default_leg_max = 2

    # ----------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>  I M P O R T A N T ! ! ! ! ! <<<<<<<<<<<<<<<<<<<<<<
    # ----------------------------------------------------------------------
    # set the amount of minimum tier-items you want to include in your output
    # this reduces the number of permutations generated if you know what you want to sim
    # if you have no clue which items do what (= sim every combination), set all to 0
    default_equip_t19_min = 0
    default_equip_t20_min = 4
    default_equip_t21_min = 0

    # quiet_mode for faster output; console is very slow
    # default 0; 1 for reduced console-output
    b_quiet = 1

    # split after n profiles
    splitting_size = 50

    # for the -sim option; if you set this to True, you won´t need to use -sim stage1
    default_sim_enabled = True
    default_sim_start_stage = "stage1"

    # these folders will be created during calculation
    # stage 1,2,3 correspond accordingly
    subdir1 = "temp_step1"
    subdir2 = "temp_step2"
    subdir3 = "temp_step3"
    # set to False if you want to keep intermediate files
    # moves the final .html-result into the specified subfolder before deletion
    # the resulting html will be renamed to: <Timestamp - best.html>
    clean_up_after_step3 = True
    result_subfolder = "results"

    # for static mode
    default_iterations_stage1 = 100
    default_iterations_stage2 = 1000
    default_iterations_stage3 = 10000

    # for dynamic mode
    # pls override this, especially stage2, if you think it is too erroneus, it depends on the chosen class/spec
    # the top100 will be simulated in stage2 and top3 in stage 3; stage1 can be chosen dynamically
    # beware: if you simulate the first stage with a very low target_error (<0.2), stage2 and stage 3 might become obsolete
    # this case might not get fully supported because of the indivduality of these problems
    default_top_n_stage2 = 100
    default_target_error_stage2 = "0.2"
    default_top_n_stage3 = 1
    default_target_error_stage3 = "0.05"

    # alternate method to determine the "best" profiles when using target_error-method
    # it does not choose fixed top n for each stage
    # instead it uses the following algorithm:
    # 1. create the list of profile-dps as usual, descending order
    # 2. if iterates the list and removes all profiles which don´t fulfil (topdps-target_error) > profiledps
    # e.g. target_error chosen in stage1 = 0.5, topdps = 1.000.000 -> it includes all profiles for stage2 with dps > 995.000
    # 3. use the same procedure for stage3
    # set this to True|False if you want to use this method
    default_use_alternate_grabbing_method = True
    # change this to widen/narrow the interval of profiles taken into account for the next stage
    default_error_rate_multiplier = 2

    # Patchwerk, LightMovement, HeavyMovement, HelterSkelter, HecticAddCleave, Ultraxion, Beastlord, CastingPatchwerk
    # https://github.com/simulationcraft/simc/wiki/RaidEvents
    default_fightstyle = "Patchwerk"

    # enter desires priority
    # low, below_normal, normal, above_normal, highest
    simc_priority = "low"
    # number of threads for simc
    # https://github.com/simulationcraft/simc/wiki/Options#multithreading
    simc_threads = 4
    # True|False
    simc_scale_factors_stage3 = True
    # 0|1
    simc_ptr = 0

    # if simc crashes, try to set this variable to "True"; it will set threads=1 and single_actor_batch=0
    # this might also output slightly different results because of single_actor_batch_now simming the input as whole raid instead of single profiles
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