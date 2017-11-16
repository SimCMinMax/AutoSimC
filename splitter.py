import os
import shutil
import sys
import subprocess
import time
import datetime
import logging
import concurrent.futures
import collections

from settings import settings
from tkinter.constants import CURRENT

# change path accordingly to your location
# don´t forget to add double-backslash for subdirs, as shown below
try:
    simc_path = settings.simc_path
except AttributeError:
    # set path after downloading nightly
    pass

subdir1 = settings.subdir1
subdir2 = settings.subdir2
subdir3 = settings.subdir3

single_actor_batch = settings.simc_single_actor_batch

user_targeterror = 0.0


# deletes and creates needed folders
# sometimes it generates a permission error; do not know why (am i removing and recreating too fast?)
def purge_subfolder(subfolder, retries=3):
    if not os.path.exists(subfolder):
        try:
            os.makedirs(subfolder)
        except PermissionError:
            if retries < 0:
                print("Error creating folders, pls check your permissions.")
                sys.exit(1)
            print("Error creating folder, retrying in 3 secs")
            time.sleep(3000)
            purge_subfolder(subfolder, retries - 1)
    else:
        shutil.rmtree(subfolder)
        purge_subfolder(subfolder, retries)


# splits generated permutation-file into n pieces
# calculations are therefore done much more memory-efficient; simcraft usually crashes the system if too many profiles
# have to be simulated at once
# inputfile: the output of main.py with all permutations in a big file
# size: after n profiles a new file will be created, incrementally numbered
#       50 seems to be a good number for this, it takes around 10-20s each, depending on simulation-parameters
def split(inputfile, size=50):
    if size <= 0:
        print("Size: " + str(size) + " is below 0")
    if os.path.isfile(inputfile):
        source = open(inputfile, "r")
        # create subfolder for first step, the splitting into n pieces
        # if exists, delete and recreate
        subfolder = os.path.join(os.getcwd(), subdir1)
        purge_subfolder(subfolder)

        output_file_number = 0
        profile_max = size
        profile_count = 0

        tempOutput = ""
        empty = True

        # true if weapon was detected so a profile-block can be closed
        # working with strings is fun!
        weapon_reached = False

        for line in source.readlines():
            if line != "\n":
                tempOutput += line

            if line.startswith("main_hand"):
                weapon_reached = True

            if line == "\n" and weapon_reached:
                profile_count += 1
                empty = False
                weapon_reached = False
                tempOutput += "\n"

            if profile_count >= profile_max:
                file = open(os.path.join(subfolder, "sim" + str(output_file_number) + ".sim"), "w")
                file.write(tempOutput)
                file.close()
                tempOutput = ""
                output_file_number += 1
                profile_count = 0
                empty = True
                weapon_reached = False

        # finish remaining profiles
        if not empty:
            file = open(os.path.join(subfolder, "sim" + str(output_file_number) + ".sim"), "w")
            file.write(tempOutput)
            file.close()
    else:
        print("Inputfile: " + str(inputfile) + " does not exist")
        sys.exit(1)


def generateCommand(file, output, sim_type, stage3, multisim, player_profile):
    cmd = []
    cmd.append(os.path.normpath(simc_path))
    cmd.append('ptr=' + str(settings.simc_ptr))
    cmd.append(file)
    cmd.append(output)
    cmd.append(sim_type)
    if multisim:
        cmd.append('threads=' + str(settings.number_of_threads))
    else:
        cmd.append('threads=' + str(settings.simc_threads))
    cmd.append('fight_style=' + str(settings.default_fightstyle))
    cmd.append('input=' + os.path.join(os.getcwd(), settings.additional_input_file))
    cmd.append('process_priority=' + str(settings.simc_priority))
    cmd.append('single_actor_batch=' + str(single_actor_batch))
    if stage3:
        if settings.simc_scale_factors_stage3:
            cmd.append('calculate_scale_factors=1')
            if player_profile.class_role == "strattack":
                cmd.append('scale_only=str,crit,haste,mastery,vers')
            elif player_profile.class_role == "agiattack":
                cmd.append('scale_only=agi,crit,haste,mastery,vers')
            elif player_profile.class_role == "spell":
                cmd.append('scale_only=int,crit,haste,mastery,vers')
    return cmd


def worker(item, counter, max):
    if settings.multi_sim_disable_console_output:
        FNULL = open(os.devnull, 'w')  # thx @cwok for working this out

    print("-----------------------------------------------------------------")
    print(F"Currently processing: {item[2]}")
    print(F"Processing: {counter+1}/{max} ({round(100 * float(int(counter) / int(max)), 1)}%)")
    try:
        duration = time.time() - starttime
        avg_calctime_hist = duration / counter
        remaining_time = (max - counter) * avg_calctime_hist
        if counter % (3 * settings.number_of_instances) == 0:
            print(F"Remaining calculation time (est.): {round(remaining_time, 0)} seconds")
            print(F"Finish time (est.): {time.asctime(time.localtime(time.time() + remaining_time))}")
    except Exception as _e:
        pass

    if settings.multi_sim_disable_console_output:
        p = subprocess.Popen(item, stdout=FNULL, stderr=FNULL)
    else:
        p = subprocess.Popen(item)
    p.wait()


def processMultiSimcCommands(commands):
    global starttime
    starttime = time.time()

    print("-----------------------------------------------------------------")
    print("Automated Simulation within AutoSimC.")
    print("Step 1 is the most time consuming, Step 2 and 3 will take ~5-20 minutes combined")
    try:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=settings.number_of_instances,
                                               thread_name_prefix="SimC-Worker")
        counter = 0
        for c in commands:
            executor.submit(worker, c, counter, len(commands))
            counter += 1
        executor.shutdown()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt in simc executor. Stopping.")
        executor.shutdown(wait=False)



# chooses settings and multi- or singlemode smartly
def sim(subdir, simtype, player_profile, command=1):
    subdir = os.path.join(os.getcwd(), subdir)
    files = os.listdir(subdir)
    files = [f for f in files if not f.endswith(".result")]
    files = [os.path.join(subdir, f) for f in files]

    start = datetime.datetime.now()
    if settings.multi_sim_enabled:
        if len(files) > 1:
            multisim(files, player_profile, simtype, command)
        else:
            singlesim(files, player_profile, simtype, command)
    else:
        singlesim(files, player_profile, simtype, command)
    end = datetime.datetime.now()
    logging.info("Simulation took {}.".format(end-start))


def multisim(files_to_sim, player_profile, simtype, command):
    output_time = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(
        datetime.datetime.now().day) + "-" + str(datetime.datetime.now().hour) + "-" + str(
        datetime.datetime.now().minute) + "-" + str(datetime.datetime.now().second)

    # some minor progress-bar-initialization
    amount_of_generated_splits = 0
    for file in files_to_sim:
        if file.endswith(".sim"):
            amount_of_generated_splits += 1

    commands = []
    for file in files_to_sim:
        if file.endswith(".sim"):
            name = file[0:file.find(".")]
            if command <= 1:
                cmd = generateCommand(file,
                                      'output=' + file + '.result',
                                      simtype,
                                      False,
                                      True,
                                      player_profile)
            if command == 2:
                cmd = generateCommand(file,
                                      'html=' + name + "-" + str(output_time) + '.html',
                                      simtype, True, True,
                                      player_profile)
            commands.append(cmd)
    processMultiSimcCommands(commands)

# Calls simcraft to simulate all .sim-files in a subdir
# simtype: 'iterations=n' or 'target_error=n'
# command: 1 for stage1 and 2, 2 for stage3 (uses html= instead of output=)
def singlesim(files_to_sim, player_profile, simtype, command=1):
    output_time = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(
        datetime.datetime.now().day) + "-" + str(datetime.datetime.now().hour) + "-" + str(
        datetime.datetime.now().minute) + "-" + str(datetime.datetime.now().second)
    starttime = time.time()

    # some minor progress-bar-initialization
    amount_of_generated_splits = 0
    for file in files_to_sim:
        if file.endswith(".sim"):
            amount_of_generated_splits += 1

    files_processed = 0
    for file in files_to_sim:
        if not file.endswith(".sim"):
            continue
        name = file[0:file.find(".")]
        if command <= 1:
            cmd = generateCommand(file,
                                  'output=' + file + '.result',
                                  simtype, False, False,
                                  player_profile)
        if command == 2:
            cmd = generateCommand(file,
                                  'html=' + name + "-" + str(output_time) + '.html',
                                  simtype, True, False,
                                  player_profile)
        print(cmd)
        print("-----------------------------------------------------------------")
        print("Automated Simulation within AutoSimC.")
        print("Currently processing: " + str(name))
        print("Processed: " + str(files_processed) + "/" + str(amount_of_generated_splits) + " (" + str(
            round(100 * float(int(files_processed) / int(amount_of_generated_splits)), 1)) + "%)")
        if files_processed > 0:
            duration = time.time() - starttime
            avg_calctime_hist = duration / files_processed
            remaining_time = (amount_of_generated_splits - files_processed) * avg_calctime_hist
            print("Remaining calculation time (est.): " + str(round(remaining_time, 0)) + " seconds")
            print("Finish time for Step 1(est.): " + time.asctime(time.localtime(time.time() + remaining_time)))
            print("Step 1 is the most time consuming, Step 2 and 3 will take ~5-20 minutes combined")
        print("-----------------------------------------------------------------")
        subprocess.call(cmd)
        files_processed += 1


def resim(subdir, player_profile):
    global user_targeterror

    print("Resimming empty files in " + str(subdir))
    if settings.skip_questions:
        mode = str(settings.auto_choose_static_or_dynamic)
    else:
        mode = input("Static (1) or dynamic mode (2)? (q to quit): ")
    if mode == "q":
        sys.exit(0)
    elif mode == "1":
        if subdir == settings.subdir1:
            iterations = settings.default_iterations_stage1
        elif subdir == settings.subdir2:
            iterations = settings.default_iterations_stage2
        elif subdir == settings.subdir3:
            iterations = settings.default_iterations_stage3
        commands = []
        for _root, _dirs, files in os.walk(os.path.join(os.getcwd(), subdir)):
            for file in files:
                if file.endswith(".sim"):
                    name = file[0:file.find(".")]
                    if (not os.path.exists(os.path.join(os.getcwd(), subdir, name + ".result"))) or os.stat(
                            os.path.join(os.getcwd(), subdir, name + ".result")).st_size <= 0:
                        cmd = generateCommand(os.path.join(os.getcwd(), subdir, name + ".sim"),
                                              'output=' + os.path.join(os.getcwd(), subdir, name) + '.result',
                                              "iterations=" + str(iterations), False, settings.multi_sim_enabled,
                                              player_profile)
                        if not settings.multi_sim_disable_console_output:
                            print("Cmd: " + str(cmd))
                        if settings.multi_sim_enabled:
                            commands.append(cmd)
                        else:
                            subprocess.call(cmd)
        if settings.multi_sim_enabled:
            processMultiSimcCommands(commands)
        return True
    elif mode == "2":
        if subdir == settings.subdir1:
            if settings.skip_questions:
                user_targeterror = settings.auto_dynamic_stage1_target_error_value
            else:
                user_targeterror = input("Which target_error?: ")
        elif subdir == settings.subdir2:
            if settings.skip_questions:
                user_targeterror = settings.default_target_error_stage2
            else:
                user_targeterror = input("Which target_error?: ")
        elif subdir == settings.subdir3:
            if settings.skip_questions:
                user_targeterror = settings.default_target_error_stage3
            else:
                user_targeterror = input("Which target_error?: ")
        commands = []
        for _root, _dirs, files in os.walk(os.path.join(os.getcwd(), subdir)):
            for file in files:
                if file.endswith(".sim"):
                    name = file[0:file.find(".")]
                    if (not os.path.exists(os.path.join(os.getcwd(), subdir, name + ".result"))) or os.stat(
                            os.path.join(os.getcwd(), subdir, name + ".result")).st_size <= 0:
                        cmd = generateCommand(os.path.join(os.getcwd(), subdir, name + ".sim"),
                                              'output=' + os.path.join(os.getcwd(), subdir, name) + '.result',
                                              "target_error=" + str(user_targeterror), False,
                                              settings.multi_sim_enabled,
                                              player_profile)
                        if not settings.multi_sim_disable_console_output:
                            print("Cmd: " + str(cmd))
                        if settings.multi_sim_enabled:
                            commands.append(cmd)
                        else:
                            subprocess.call(cmd)
        if settings.multi_sim_enabled:
            processMultiSimcCommands(commands)
        return True
    return False


# determine best n dps-simulations and grabs their profiles for further simming
# count: number of top n dps-simulations
# source_subdir: directory of .result-files
# target_subdir: directory to store the resulting .sim-file
# origin: path to the originally in autosimc generated output-file containing all valid profiles
def grabBest(count, source_subdir, target_subdir, origin):
    print("Grabbest:")
    print("Variables: Top n: " + str(count))
    print("Variables: source_subdir: " + str(source_subdir))
    print("Variables: target_subdir: " + str(target_subdir))
    print("Variables: origin: " + str(origin))

    user_class = ""

    best = {}
    for _root, _dirs, files in os.walk(os.path.join(os.getcwd(), source_subdir)):
        for file in files:
            # print("Grabbest -> file: " + str(file))
            if file.endswith(".result"):
                if os.stat(os.path.join(os.getcwd(), source_subdir, file)).st_size > 0:
                    src = open(os.path.join(os.getcwd(), source_subdir, file), encoding='utf-8', mode="r")
                    for line in src.readlines():
                        line = line.lstrip().rstrip()
                        if not line:
                            continue
                        if line.rstrip().startswith("Raid"):
                            continue
                        if line.rstrip().startswith("raid_event"):
                            continue
                        if line.rstrip().startswith("HPS"):
                            continue
                        if line.rstrip().startswith("DPS"):
                            continue
                        # here parsing stops, because its useless profile-junk
                        if line.rstrip().startswith("DPS:"):
                            break
                        if line.rstrip().endswith("Raid"):
                            continue
                        # just get user_class from player_info, very dirty
                        if line.rstrip().startswith("Player"):
                            q, w, e, r, t, z = line.split()
                            user_class = r
                            break
                        # dps, percentage, profilename
                        a, _b, c = line.lstrip().rstrip().split()
                        # print("Splitted_lines = a: "+str(a)+" b: "+str(b)+" c: "+str(c))
                        # put dps as key and profilename as value into dictionary
                        # dps might be equal for 2 profiles, but should very rarely happen
                        # could lead to a problem with very minor dps due to variance,
                        # but seeing dps going into millions nowadays equal dps should not pose to be a problem at all
                        best[a] = c
                    src.close()
                else:
                    print("Error: .result-file in: " + str(source_subdir) + " is empty, exiting")
                    sys.exit(1)

    # put best dps into a list, descending order
    sortedlist = []
    for entry in best.keys():
        sortedlist.append(int(entry))
    sortedlist.sort()
    sortedlist.reverse()
    # print(str(sortedlist))

    # trim list to desired number
    while len(sortedlist) > count:
        sortedlist.pop()

    # print("Sortedlist: "+str(sortedlist))
    # and finally generate a second list with the corresponding profile-names
    sortednames = []
    while len(sortedlist) > 0:
        sortednames.append(best.get(str(sortedlist.pop())))
    # print("Sortednames: "+str(sortednames))

    bestprofiles = []
    # print(str(bestprofiles))

    subfolder = os.path.join(os.getcwd(), target_subdir)
    purge_subfolder(subfolder)
    filenumber = 1

    # now parse our "database" and extract the profiles of our top n
    source = open(origin, "r")
    lines = source.readlines()
    lines_iter = iter(lines)

    for line in lines_iter:
        line = line.lstrip().rstrip()
        if not line:
            continue

        currentbestprofile = ""

        if line.startswith(user_class + "="):
            _classname, profilename = line.split("=")
            if profilename in sortednames:
                currentbestprofile += line + "\n"
                line = next(lines_iter)
                while not line.startswith(user_class + "="):
                    try:
                        currentbestprofile += line
                        line = next(lines_iter)
                    except StopIteration:
                        break
                bestprofiles.append(currentbestprofile)
        if target_subdir == settings.subdir2:
            amount = settings.number_of_instances if settings.multi_sim_enabled else settings.splitting_size
        else:
            amount = settings.splitting_size
        if len(bestprofiles) > amount:
            with open(os.path.join(os.getcwd(), target_subdir, "best" + str(filenumber) + ".sim"), "w") as out:
                for line in bestprofiles:
                    out.write(line)
                filenumber += 1
            bestprofiles.clear()

    logging.info("Got {} best profiles.".format(len(bestprofiles)))
    if len(bestprofiles) > 0:
        with open(os.path.join(os.getcwd(), target_subdir, "best" + str(filenumber) + ".sim"), "w") as out:
            for line in bestprofiles:
                out.write(line)

    source.close()


def dump_profiles_to_file(filename, profiles):
    logging.debug("Writing {} profiles to file {}.".format(len(profiles), filename))
    with open(filename, "w") as out:
        for line in profiles:
            out.write(line)


def parse_profiles_from_file(fd, user_class):
    """Parse a simc file, and yield each player entry (between two class=name lines)"""
    current_profile = []
    for line in fd:
        line = line.rstrip()  # Remove trailing \n
        if line.startswith(user_class + "="):
            if len(current_profile):
                yield current_profile
                current_profile = []
        current_profile.append(line)
    # Add tail
    if len(current_profile):
        yield current_profile


# determine best n dps-simulations and grabs their profiles for further simming
# targeterror: the span which removes all profile-dps not fulfilling it (see settings.py)
# source_subdir: directory of .result-files
# target_subdir: directory to store the resulting .sim-file
# origin: path to the originally in autosimc generated output-file containing all valid profiles
def grabBestAlternate(targeterror, source_subdir, target_subdir, origin):
    print("Grabbest:")
    print("Variables: targeterror: " + str(targeterror))
    print("Variables: target_subdir: " + str(target_subdir))
    print("Variables: origin: " + str(origin))

    user_class = ""

    best = []
    source_subdir = os.path.join(os.getcwd(), source_subdir)
    print("Variables: source_subdir: " + str(source_subdir))
    files = os.listdir(source_subdir)
    files = [f for f in files if f.endswith(".result")]
    files = [os.path.join(source_subdir, f) for f in files]
    logging.debug("Grabbing files: {}".format(files))

    for file in files:
        if os.stat(file).st_size <= 0:
            raise RuntimeError("Error: .result-file in: " + str(source_subdir) + " is empty, exiting")

        with open(file, encoding='utf-8', mode="r") as src:
            for line in src.readlines():
                line = line.lstrip().rstrip()
                if not line:
                    continue
                if line.rstrip().startswith("Raid"):
                    continue
                if line.rstrip().startswith("raid_event"):
                    continue
                if line.rstrip().startswith("HPS"):
                    continue
                if line.rstrip().startswith("DPS"):
                    continue
                # here parsing stops, because its useless profile-junk
                if line.rstrip().startswith("DPS:"):
                    break
                if line.rstrip().endswith("Raid"):
                    continue
                # just get user_class from player_info, very dirty
                if line.rstrip().startswith("Player"):
                    q, w, e, r, t, z = line.split()
                    user_class = r
                    break
                # dps, percentage, profilename
                dps, _pct, profile_name = line.lstrip().rstrip().split()
                # print("Splitted_lines = a: "+str(a)+" b: "+str(b)+" c: "+str(c))
                # put dps as key and profilename as value into dictionary
                # dps might be equal for 2 profiles, but should very rarely happen
                # could lead to a problem with very minor dps due to variance,
                # but seeing dps going into millions nowadays equal dps should not pose to be a problem at all
                best.append((float(dps), profile_name))

    # sort best dps, descending order
    best = list(reversed(sorted(best, key=lambda entry: entry[0])))
    logging.debug("Result from parsing dps len={}".format(len(best)))
    for dps, name in best:
        logging.debug("{}: {}".format(dps, name))

    # remove all profiles not within the errorrange
    if len(best) > 2:
        dps_best_player = best[0][0]
        dps_min = dps_best_player * (1.0 - (settings.default_error_rate_multiplier * targeterror) / 100.0)
        logging.debug("Filtering out all players below dps_min={}".format(dps_min))
        best = [e for e in best if e[0] >= dps_min]

    logging.debug("Filtered dps results len={}".format(len(best)))
    for dps, name in best:
        logging.debug("{}: {}".format(dps, name))

    sortednames = [name for _dps, name in best]

    bestprofiles = []
    outfile_count = 0
    num_profiles = 0
    # print(str(bestprofiles))

    # Determine chunk length we want to split the profiles
    if target_subdir == settings.subdir2:
        if settings.multi_sim_enabled:
            chunk_length = int(len(sortednames) // settings.number_of_instances)+1
    else:
        chunk_length = settings.splitting_size
    if chunk_length < 1:
        chunk_length = 1
    if chunk_length > settings.splitting_size:
        chunk_length = settings.splitting_size
    logging.debug("Chunk length: {}".format(chunk_length))

    # now parse our "database" and extract the profiles of our top n
    logging.debug("Getting sim input from file {}.".format(origin))
    with open(origin, "r") as source:
        subfolder = os.path.join(os.getcwd(), target_subdir)
        purge_subfolder(subfolder)
        for profile in parse_profiles_from_file(source, user_class):
            _classname, profilename = profile[0].split("=")
            if profilename in sortednames:
                profile.append("")  # Add tailing empty line
                bestprofiles.append("\n".join(profile))
                num_profiles += 1
                logging.debug("Added {} to best list.".format(profilename))
                # If we reached chunk length, dump collected profiles and reset, so we do not store everything in memory
                if len(bestprofiles) >= chunk_length:
                    outfile = os.path.join(os.getcwd(), target_subdir, "best" + str(outfile_count) + ".sim")
                    dump_profiles_to_file(outfile, bestprofiles)
                    bestprofiles.clear()
                    outfile_count += 1

    # Write tail
    if len(bestprofiles):
        outfile = os.path.join(os.getcwd(), target_subdir, "best" + str(outfile_count) + ".sim")
        dump_profiles_to_file(outfile, bestprofiles)
        outfile_count += 1

    logging.info("Got {} best profiles written to {} files..".format(num_profiles, outfile_count))
