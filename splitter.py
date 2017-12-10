import os
import shutil
import sys
import subprocess
import time
import datetime
import logging
import concurrent.futures
import re
import math

from settings import settings


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


def dump_profiles_to_file(filename, profiles):
    logging.debug("Writing {} profiles to file {}.".format(len(profiles), filename))
    with open(filename, "w") as out:
        for line in profiles:
            out.write(line)


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


def split(inputfile, destination_folder, size, wow_class):
    """
    Split a .simc file into n pieces
    calculations are therefore done much more memory-efficient; simcraft usually crashes the system if too many profiles
    have to be simulated at once
    inputfile: the output of main.py with all permutations in a big file
    size: after size profiles a new file will be created, incrementally numbered
    """
    if size <= 0:
        raise ValueError("Invalid split size {} <= 0.".format(size))
    logging.info("Splitting profiles in {} into chunks of size {}.".format(inputfile, size))
    print("This may take a while...")
    logging.debug("wow_class={}".format(wow_class))

    num_profiles = 0
    bestprofiles = []
    outfile_count = 0
    purge_subfolder(destination_folder)
    with open(inputfile, encoding='utf-8', mode="r") as src:
        for profile in parse_profiles_from_file(src, wow_class):
            profile.append("")  # Add tailing empty line
            bestprofiles.append("\n".join(profile))
            if len(bestprofiles) >= size:
                outfile = os.path.join(destination_folder, "sim" + str(outfile_count) + ".sim")
                dump_profiles_to_file(outfile, bestprofiles)
                num_profiles += len(bestprofiles)
                bestprofiles.clear()
                outfile_count += 1
    # Write tail
    if len(bestprofiles):
        outfile = os.path.join(destination_folder, "sim" + str(outfile_count) + ".sim")
        dump_profiles_to_file(outfile, bestprofiles)
        outfile_count += 1
        num_profiles += len(bestprofiles)
    return num_profiles


def generateCommand(file, outputs, sim_type, simtype_value, is_last_stage, player_profile, num_files_to_sim):
    cmd = []
    cmd.append(os.path.normpath(settings.simc_path))
    if bool(settings.simc_ptr):
        cmd.append('ptr=' + str(int(settings.simc_ptr)))
    cmd.append(file)
    for output in outputs:
        cmd.append(output)
    cmd.append("{}={}".format(sim_type, simtype_value))
    if num_files_to_sim > 1:
        cmd.append('threads=' + str(settings.number_of_threads))
    else:
        cmd.append('threads=' + str(settings.simc_threads))
    cmd.append('fight_style=' + str(settings.default_fightstyle))
    cmd.append('input=' + os.path.join(os.getcwd(), settings.additional_input_file))
    cmd.append('process_priority=' + str(settings.simc_priority))
    cmd.append('single_actor_batch=' + str(settings.simc_single_actor_batch))

    # For simulations with a high target_error, we want to get a faster execution (eg. only 47 iterations)
    # instead of the default minimum of ~100 iterations. This options tells SimC to more often check target_error
    # condition while simulating.
    if sim_type is "target_error" and simtype_value > 0.1:
        cmd.append('analyze_error_interval=10')

    if is_last_stage:
        if settings.simc_scale_factors_last_stage:
            cmd.append('calculate_scale_factors=1')
            if player_profile.class_role == "strattack":
                cmd.append('scale_only=str,crit,haste,mastery,vers')
            elif player_profile.class_role == "agiattack":
                cmd.append('scale_only=agi,crit,haste,mastery,vers')
            elif player_profile.class_role == "spell":
                cmd.append('scale_only=int,crit,haste,mastery,vers')
    return cmd


def worker(command, counter, maximum, starttime, num_workers):
    print("-----------------------------------------------------------------")
    print("Currently processing: {}".format(command[2]))
    print("Processing: {}/{} ({}%)".format(counter + 1,
                                           maximum,
                                           round(100 * float(int(counter) / int(maximum)), 1)))
    try:
        if counter > 0 and counter % num_workers == 0:
            duration = datetime.datetime.now() - starttime
            avg_calctime_hist = duration / counter
            remaining_time = (maximum - counter) * avg_calctime_hist
            finish_time = datetime.datetime.now() + remaining_time
            print("Remaining calculation time (est.): {}.".format(remaining_time))
            print("Finish time (est.): {}".format(finish_time))
    except Exception:
        logging.debug("Error while calculating progress time.", exc_info=True)

    if settings.multi_sim_disable_console_output and maximum > 1:
        FNULL = open(os.devnull, 'w')  # thx @cwok for working this out
        p = subprocess.Popen(command, stdout=FNULL, stderr=FNULL)
    else:
        p = subprocess.Popen(command)
    r = p.wait()
    if r != 0:
        logging.error("Simulation #{} returned error code {}.".format(counter, r))
    return r


def launch_simc_commands(commands):
    starttime = datetime.datetime.now()

    print("-----------------------------------------------------------------")
    print("Starting multi-process simulation.")
    print("Number of work items: {}.".format(len(commands)))
    print("Number of worker instances: {}.".format(settings.number_of_instances))
    logging.debug("Starting simc with commands={}".format(commands))
    try:
        num_workers = settings.number_of_instances
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_workers)
        counter = 0
        results = []
        for command in commands:
            results.append(executor.submit(worker, command, counter, len(commands), starttime, num_workers))
            counter += 1

        # Check if we got any simulations with error code != 0. futures.as_completed gives us the results as soon as a
        # simulation is finished.
        for future in concurrent.futures.as_completed(results):
            r = int(future.result())
            if r != 0:
                logging.error("Invalid return code from SimC: {}".format(r))
                # Hacky way to shut down all remaining sims, apparently just calling shutdown(wait=False0 on the
                # executor does not have the same effect.
                for f in results:
                    f.cancel()
                executor.shutdown(wait=False)
                return False
        executor.shutdown()
        return True
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt in simc executor. Stopping.")
        for f in results:
            f.cancel()
        executor.shutdown(wait=False)
        raise
    return False


def start_multi_sim(files_to_sim, player_profile, simtype, simtype_value, stage, is_last_stage, num_profiles):
    output_time = "{:%Y-%m-%d_%H-%M-%S}".format(datetime.datetime.now())

    # some minor progress-bar-initialization
    amount_of_generated_splits = 0
    for file in files_to_sim:
        if file.endswith(".sim"):
            amount_of_generated_splits += 1

    num_files_to_sim = len(files_to_sim)

    commands = []
    for file in files_to_sim:
        if file.endswith(".sim"):
            name = file[0:file.find(".")]
            outputs = ['output=' + file + '.result']
            if num_files_to_sim == 1 or is_last_stage:
                outputs.append('html=' + name + "-" + str(output_time) + '.html')
            cmd = generateCommand(file,
                                  outputs,
                                  simtype,
                                  simtype_value,
                                  is_last_stage,
                                  player_profile,
                                  num_files_to_sim)
            commands.append(cmd)
    return launch_simc_commands(commands)


# chooses settings and multi- or singlemode smartly
def sim(subdir, simtype, simtype_value, player_profile, stage, is_last_stage, num_profiles):
    logging.info("Starting simulation.")
    logging.debug("Started simulation with {}".format(locals()))
    subdir = os.path.join(os.getcwd(), subdir)
    files = os.listdir(subdir)
    files = [f for f in files if not f.endswith(".result")]
    files = [os.path.join(subdir, f) for f in files]

    start = datetime.datetime.now()
    result = start_multi_sim(files, player_profile, simtype, simtype_value, stage, is_last_stage, num_profiles)
    end = datetime.datetime.now()
    logging.info("Simulation took {}.".format(end - start))
    return result


def filter_by_length(dps_results, n):
    """
    filter dps list to only contain n results
    dps_results is a pre-sorted list (dps, name) in descending order
    """
    return dps_results[:n]


def filter_by_target_error(dps_results, target_error):
    """
    remove all profiles not within the errorrange of the best player
    dps_results is a pre-sorted list (dps, name) in descending order
    """
    output = dps_results
    if len(dps_results) > 2:
        output = []
        dps_best_player = dps_results[0]["dps"]
        dps_error_best_player = dps_results[0]["dps_error"]
        for entry in dps_results:
            dps = entry["dps"]
            err = entry["dps_error"]
            # if dps difference is less than sqrt(err_best**2+err**2) * error_mult, keep result
            if dps_best_player - dps < math.sqrt(err ** 2 + dps_error_best_player ** 2) * settings.default_error_rate_multiplier:
                output.append(entry)
    return output


# determine best n dps-simulations and grabs their profiles for further simming
# targeterror: the span which removes all profile-dps not fulfilling it (see settings.py)
# source_subdir: directory of .result-files
# target_subdir: directory to store the resulting .sim-file
# origin: path to the originally in autosimc generated output-file containing all valid profiles
def grab_best(filter_by, filter_criterium, source_subdir, target_subdir, origin, split_optimally=True):
    print("Grabbest:")
    print("Variables: filter by: " + str(filter_by))
    print("Variables: filter_criterium: " + str(filter_criterium))
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

    start = datetime.datetime.now()
    dps_regex = re.compile("  DPS: (\d+\.\d+)  DPS-Error=(\d+\.\d+)/(\d+\.\d+)%")
    for file in files:
        if os.stat(file).st_size <= 0:
            raise RuntimeError("Error: result file '{}' is empty, exiting.".format(file))

        with open(file, encoding='utf-8', mode="r") as src:
            current_player = {}
            for line in src:
                if line.startswith("Player: "):
                    _player, profile_name, _race, wow_class, *_tail = line.split()
                    user_class = wow_class
                    current_player["name"] = profile_name
                if line.startswith("  DPS: "):
                    match = dps_regex.search(line)
                    if not match:
                        raise ValueError("Invalid SimC result file. DPS information could not be parsed.")
                    dps, dps_error, dps_error_pct = match.groups()
                    if "name" not in current_player:
                        # DPS entry does not belong to "Player". (eg. "Target")
                        continue
                    current_player["dps"] = float(dps)
                    current_player["dps_error"] = float(dps_error)
                    current_player["dps_error_pct"] = dps_error_pct
                    best.append(current_player)
                    current_player = {}

    logging.debug("Parsing input files for dps took: {}".format(datetime.datetime.now() - start))

    # sort best dps, descending order
    best = list(reversed(sorted(best, key=lambda entry: entry["dps"])))
    logging.debug("Result from parsing dps len={}".format(len(best)))

    if filter_by == "target_error":
        best = filter_by_target_error(best, filter_criterium)
    elif filter_by == "count":
        best = filter_by_length(best, filter_criterium)
    else:
        raise ValueError("Invalid filter")

    logging.debug("Filtered dps results len={}".format(len(best)))
    for entry in best:
        logging.debug("{}".format(entry))

    sortednames = [entry["name"] for entry in best]
    print(sortednames)

    bestprofiles = []
    outfile_count = 0
    num_profiles = 0
    # print(str(bestprofiles))

    # Determine chunk length we want to split the profiles
    if split_optimally:
        chunk_length = int(len(sortednames) // settings.number_of_instances) + 1
    else:
        chunk_length = int(settings.splitting_size)
    if chunk_length < 1:
        chunk_length = 1
    if chunk_length > int(settings.splitting_size):
        chunk_length = int(settings.splitting_size)
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
    return num_profiles
