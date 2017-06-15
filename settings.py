class settings():
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
    # if you have no clue which items do what (= sim every combination), set both to 0
    default_equip_t19_min = 4
    default_equip_t20_min = 0

    # quiet_mode for faster output; console is very slow
    # default 0; 1 for reduced console-output
    b_quiet = 1

    # split after n profiles
    splitting_size = 50

    # for the -sim option
    # path to your simcraft .exe
    # don´t forget to include double-backslash for subfolders
    simc_path = 'D:\\Downloads\\simc-725-01-win64-729a0f8\\simc-725-01-win64\\simc.exe'
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
    default_top_n_stage3 = 3
    default_target_error_stage3 = "0.05"

    # Patchwerk, LightMovement, HeavyMovement, HelterSkelter, HecticAddCleave
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
    simc_safe_mode = False
    # you want this to be set to 1 most of the time; it is used if you want to simulate a whole raid instead of
    # single profiles,
    simc_single_actor_batch=1
    # additional input you might want to sim according to
    # https://github.com/simulationcraft/simc/wiki/TextualConfigurationInterface
    # the file must be present in the autosimc-folder
    # if you don´t want to use this, set it no "nul"
    additional_input_file = "nul"
    # additional_input_file= "additional_input.txt"

    # For Analysis.py
    # set to "nul" if you are simulating healer or tanks
    analyzer_path = "profiles"
    analyzer_filename = "Analysis.json"