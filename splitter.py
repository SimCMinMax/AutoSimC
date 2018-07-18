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
try:
    from settings_local import settings
except ImportError:
    pass

import gettext
gettext.install('AutoSimC')


def _parse_profiles_from_file(fd, user_class):
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


def _dump_profiles_to_file(filename, profiles):
    logging.debug("Writing {} profiles to file {}.".format(len(profiles), filename))
    with open(filename, "w") as out:
        for line in profiles:
            out.write(line)


def _purge_subfolder(subfolder):
    """Deletes and creates needed subfolders"""
    if not os.path.exists(subfolder):
        try:
            os.makedirs(subfolder)
        except Exception as e:
            raise RuntimeError(_("Error creating subfolder '{}': {}.").format(e)) from e
    else:
        # Avoid PermissionError when re-creating directory directly after deleting the tree.
        # See https://stackoverflow.com/a/16375240
        tmp_name = subfolder + "_tmp"
        os.rename(subfolder, tmp_name)
        try:
            shutil.rmtree(tmp_name)
        finally:
            os.makedirs(subfolder)


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
    _purge_subfolder(destination_folder)
    with open(inputfile, encoding='utf-8', mode="r") as src:
        for profile in _parse_profiles_from_file(src, wow_class):
            profile.append("")  # Add tailing empty line
            bestprofiles.append("\n".join(profile))
            if len(bestprofiles) >= size:
                outfile = os.path.join(destination_folder, "sim" + str(outfile_count) + ".simc")
                _dump_profiles_to_file(outfile, bestprofiles)
                num_profiles += len(bestprofiles)
                bestprofiles.clear()
                outfile_count += 1
    # Write tail
    if len(bestprofiles):
        outfile = os.path.join(destination_folder, "sim" + str(outfile_count) + ".simc")
        _dump_profiles_to_file(outfile, bestprofiles)
        outfile_count += 1
        num_profiles += len(bestprofiles)
    return num_profiles


def _prepare_fight_style(player_profile, cmd):
    # for now i overwrite additional_input.txt as it is relatively easy to edit the .json containing the profiles
    # maybe concatenation could be possible? imho it would lead to more problems if a custom profile was loaded
    # while additional_input contains even more custom commands
    # i see however the appeal for e.g. appending a additional_input_2.txt containing only overrides
    # default_profiles do not contain any additional lines, so they can be appended to the command line easily
    if player_profile.fightstyle["name"].startswith("Default"):
        cmd.append('fight_style=' + str(player_profile.fightstyle["command"]))
    else:
        with open(settings.additional_input_file, "w") as file:
            for entry in player_profile.fightstyle:
                if entry.startswith("line"):
                    file.write(player_profile.fightstyle[entry]+"\n")
            cmd.append('input=\"{}\"'.format(os.path.join(os.getcwd(), settings.additional_input_file)))
    return cmd


def _generate_sim_options(output_file, sim_type, simtype_value, is_last_stage, player_profile, num_files_to_sim):
    """Generate global (per stage) simc options and write them to .simc output file"""
    cmd = []
    if bool(settings.simc_ptr):
        cmd.append('ptr=' + str(int(settings.simc_ptr)))
    cmd.append("{}={}".format(sim_type, simtype_value))
    if num_files_to_sim > 1 and not is_last_stage:
        cmd.append('threads=' + str(settings.number_of_threads))
    else:
        cmd.append('threads=' + str(settings.simc_threads))
    cmd = _prepare_fight_style(player_profile, cmd)
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
    logging.info("Commandline: {}".format(cmd))
    with open(output_file, "w") as f:
        f.write(" ".join(cmd))


def _generateCommand(file, global_option_file, outputs):
    """Generate command line arguments to invoke SimulationCraft"""
    cmd = []
    cmd.append(os.path.normpath(settings.simc_path))
    cmd.append("input={}".format(global_option_file))
    cmd.append("input={}".format(file))
    for output in outputs:
        cmd.append(output)
    return cmd


def _worker(command, counter, maximum, starttime, num_workers):
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

    if settings.multi_sim_disable_console_output and maximum > 1 and num_workers > 1:
        p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        p = subprocess.run(command)
    if p.returncode != 0:
        logging.error("SimulationCraft error! Worker #{} returned error code {}.".format(counter, p.returncode))
        if settings.multi_sim_disable_console_output and maximum > 1 and num_workers > 1:
            logging.info("SimulationCraft #{} stderr: \n{}".format(counter, p.stderr.read().decode()))
            logging.debug("SimulationCraft #{} stdout: \n{}".format(counter, p.stdout.read().decode()))
    return p.returncode


def _launch_simc_commands(commands, is_last_stage):
    starttime = datetime.datetime.now()

    if is_last_stage:
        num_workers = 1
    else:
        num_workers = settings.number_of_instances
    print("-----------------------------------------------------------------")
    logging.info("Starting multi-process simulation.")
    logging.info("Number of work items: {}.".format(len(commands)))
    logging.info("Number of worker instances: {}.".format(num_workers))
    logging.debug("Starting simc with commands={}".format(commands))
    try:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_workers)
        counter = 0
        results = []
        for command in commands:
            results.append(executor.submit(_worker, command, counter, len(commands), starttime, num_workers))
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
        logging.warning("KeyboardInterrupt in simc executor. Stopping.")
        for f in results:
            f.cancel()
        executor.shutdown(wait=False)
        raise
    return False


def _start_simulation(files_to_sim, player_profile, simtype, simtype_value, stage, is_last_stage, num_profiles):
    output_time = "{:%Y-%m-%d_%H-%M-%S}".format(datetime.datetime.now())

    # some minor progress-bar-initialization
    amount_of_generated_splits = 0
    for file in files_to_sim:
        if file.endswith(".simc"):
            amount_of_generated_splits += 1

    num_files_to_sim = len(files_to_sim)
    if num_files_to_sim == 0:
        raise ValueError("Number of files to sim in stage {} is 0. Check path (spaces? special chars?)".format(stage))

    # First generate global simc options
    base_path, _filename = os.path.split(files_to_sim[0])
    sim_options = os.path.join(base_path, "arguments.simc")
    _generate_sim_options(sim_options, simtype, simtype_value, is_last_stage, player_profile, num_files_to_sim)

    # Generate arguments for launching simc for each splitted file
    commands = []
    for file in files_to_sim:
        if file.endswith(".simc"):
            base_path, filename = os.path.split(file)
            basename, _extension = os.path.splitext(filename)
            outputs = ['output=' + os.path.join(base_path, basename + '.result')]
            if num_files_to_sim == 1 or is_last_stage:
                html_file = os.path.join(base_path, str(output_time) + "-" + basename + ".html")
                outputs.append('html={}'.format(html_file))
            cmd = _generateCommand(file,
                                  sim_options,
                                  outputs)
            commands.append(cmd)
    return _launch_simc_commands(commands, is_last_stage)


def simulate(subdir, simtype, simtype_value, player_profile, stage, is_last_stage, num_profiles):
    """Start the simulation process for a given stage/input"""
    logging.info("Starting simulation.")
    logging.debug("Started simulation with {}".format(locals()))
    subdir = os.path.join(os.getcwd(), subdir)
    files = os.listdir(subdir)
    files = [f for f in files if not f.endswith(".result")]
    files = [os.path.join(subdir, f) for f in files]

    start = datetime.datetime.now()
    result = _start_simulation(files, player_profile, simtype, simtype_value, stage, is_last_stage, num_profiles)
    end = datetime.datetime.now()
    logging.info("Simulation took {}.".format(end - start))
    return result


def _filter_by_length(metric_results, n):
    """
    filter metric(dps/hps/tmi) list to only contain n results
    dps_results is a pre-sorted list (dps, name) in descending order
    """
    return metric_results[:n]


def _filter_by_target_error(metric_results):
    """
    remove all profiles not within the errorrange of the best player
    metric_results is a pre-sorted list (dps/hps/tmi, name) in descending order
    """
    output = metric_results
    if len(metric_results) > 2:
        output = []
        metric_best_player = metric_results[0]["metric"]
        metric_error_best_player = metric_results[0]["metric_error"]
        if metric_error_best_player == 0:
            raise ValueError(_("Metric error of best player {} is zero. Cannot filter by target_error.")
                             .format(metric_results[0]["name"]))
        for entry in metric_results:
            metric = entry["metric"]
            err = entry["metric_error"]
            # if dps difference is less than sqrt(err_best**2+err**2) * error_mult, keep result
            if metric_best_player - metric < math.sqrt(
                    err ** 2 + metric_error_best_player ** 2) * settings.default_error_rate_multiplier:
                output.append(entry)
    return output


def grab_best(filter_by, filter_criterium, source_subdir, target_subdir, origin, split_optimally=True):
    """Determine best simulations and grabs their profiles for further simming"""
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
    metric = settings.select_by_metric
    logging.info("Selecting by metric: '{}'.".format(metric))
    metric_regex = re.compile("\s*{metric}=(\d+\.\d+) {metric}-error=(\d+\.\d+)/(\d+\.\d+)%".format(metric=metric), re.IGNORECASE)
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
                match = metric_regex.search(line)
                if not match:
                    continue
                metric_value, metric_error, metric_error_pct = match.groups()
                if "name" not in current_player:
                    # metric entry does not belong to "Player". (eg. "Target")
                    continue
                current_player["metric"] = float(metric_value)
                current_player["metric_error"] = float(metric_error)
                current_player["metric_error_pct"] = metric_error_pct
                best.append(current_player)
                current_player = {}

    logging.debug("Parsing input files for {} took: {}".format(metric, datetime.datetime.now() - start))

    # sort best metric, descending order
    best = list(reversed(sorted(best, key=lambda entry: entry["metric"])))
    logging.debug("Result from parsing {} with metric '{}' len={}".format(metric, metric, len(best)))

    if filter_by == "target_error":
        filterd_best = _filter_by_target_error(best)
    elif filter_by == "count":
        filterd_best = _filter_by_length(best, filter_criterium)
    else:
        raise ValueError("Invalid filter")

    logging.debug("Filtered metric results len={}".format(len(filterd_best)))
    for entry in filterd_best:
        logging.debug("{}".format(entry))

    sortednames = [entry["name"] for entry in filterd_best]

    if len(filterd_best) == 0:
        raise RuntimeError(_("Could not grab any valid profiles from previous run."
                             " ({} profiles available before filtering, {} after filtering)")
                           .format(len(best), len(filterd_best)))

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

    if not os.path.exists(target_subdir):
        os.makedirs(target_subdir)

    # now parse our "database" and extract the profiles of our top n
    logging.debug("Getting sim input from file {}.".format(origin))
    with open(origin, "r") as source:
        subfolder = target_subdir
        _purge_subfolder(subfolder)
        for profile in _parse_profiles_from_file(source, user_class):
            _classname, profilename = profile[0].split("=")
            if profilename in sortednames:
                profile.append("")  # Add tailing empty line
                bestprofiles.append("\n".join(profile))
                num_profiles += 1
                logging.debug("Added {} to best list.".format(profilename))
                # If we reached chunk length, dump collected profiles and reset, so we do not store everything in memory
                if len(bestprofiles) >= chunk_length:
                    outfile = os.path.join(target_subdir, "best" + str(outfile_count) + ".simc")
                    _dump_profiles_to_file(outfile, bestprofiles)
                    bestprofiles.clear()
                    outfile_count += 1

    # Write tail
    if len(bestprofiles):
        outfile = os.path.join(target_subdir, "best" + str(outfile_count) + ".simc")
        _dump_profiles_to_file(outfile, bestprofiles)
        outfile_count += 1

    logging.info(_("Got {} best profiles written to {} files..").format(num_profiles, outfile_count))
    return num_profiles
