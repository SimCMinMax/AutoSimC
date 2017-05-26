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

    # quiet_mode for faster output; console is very slow
    # default 0; 1 for reduced console-output
    b_quiet = 1

    # split after n profiles
    splitting_size = 50

    # for the -sim option
    # path to your simcraft .exe
    # don´t forget to include double-backslash for subfolders
    simc_path= 'D:\\Downloads\\simc-720-03-win64-6bfab13\\simc-720-03-win64\\simc.exe'
    # these folders will be created during calculation
    # stage 1,2,3 correspond accordingly
    subdir1 = "temp_step1"
    subdir2 = "temp_step2"
    subdir3 = "temp_step3"


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

    # For Analysis.py
    analyzer_path = "profiles"
    analyzer_filename = "Analysis.json"
