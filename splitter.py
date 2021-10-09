from dataclasses import dataclass
import os
import subprocess
import datetime
import logging
import concurrent.futures
import re
import math
from typing import List, Optional

from settings import settings
try:
    from settings_local import settings
except ImportError:
    pass

from i18n import _
from profile import Profile, load_multiple_profiles


def _parse_profiles_from_file(fd, user_class):
    """Parse a simc file, and yield each player entry (between two class=name lines)"""
    current_profile = []
    for line in fd:
        line = line.rstrip()  # Remove trailing \n
        if line.startswith(user_class + "="):
            if current_profile:
                yield current_profile
                current_profile = []
        current_profile.append(line)
    # Add tail
    if current_profile:
        yield current_profile


def _dump_profiles_to_file(filename, profiles):
    logging.debug("Writing {} profiles to file {}.".format(len(profiles), filename))
    with open(filename, "w") as out:
        for line in profiles:
            out.write(line)


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


@dataclass
class SimcOptions:
    player_profile: Profile
    is_last_stage: bool
    target_error: Optional[float] = None
    iterations: Optional[int] = None

    @property
    def sim_options(self) -> str:
        cmd = []
        if settings.simc_ptr:
            cmd.append('ptr=1')
        if self.target_error:
            cmd.append(f'target_error={self.target_error}')
        elif self.iterations:
            cmd.append(f'iterations={self.iterations}')
        else:
            raise ValueError('Either target_error or iterations must be set')
        cmd.extend(self.player_profile.fight_style.simc_options)
        cmd.append(f'process_priority={settings.simc_priority}')
        cmd.append(f'single_actor_batch={settings.simc_single_actor_batch}')

        # For simulations with a high target_error, we want to get a faster
        # execution (eg. only 47 iterations) instead of the default minimum of
        # ~100 iterations. This options tells SimC to more often check
        # target_error condition while simulating.
        if self.target_error and self.target_error > 0.1:
            cmd.append('analyze_error_interval=10')

        if self.is_last_stage and settings.simc_scale_factors_last_stage:
            cmd.append('calculate_scale_factors=1')
            if self.player_profile.class_role == 'strattack':
                cmd.append('scale_only=str,crit,haste,mastery,vers')
            elif self.player_profile.class_role == 'agiattack':
                cmd.append('scale_only=agi,crit,haste,mastery,vers')
            elif self.player_profile.class_role == 'spell':
                cmd.append('scale_only=int,crit,haste,mastery,vers')

        return ' '.join(cmd)


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
        p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    else:
        p = subprocess.run(command, text=True)
    if p.returncode != 0:
        logging.error("SimulationCraft error! Worker #{} returned error code {}.".format(counter, p.returncode))
        if settings.multi_sim_disable_console_output and maximum > 1 and num_workers > 1:
            logging.info("SimulationCraft #{} stderr: \n{}".format(counter, p.stderr))
            logging.debug("SimulationCraft #{} stdout: \n{}".format(counter, p.stdout))
    return p.returncode


def _launch_simc_commands(commands, is_last_stage):
    starttime = datetime.datetime.now()
    results = []
    num_workers = 1 if is_last_stage else settings.number_of_instances
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_workers)
    print("-----------------------------------------------------------------")
    logging.info("Starting multi-process simulation.")
    logging.info("Number of work items: {}.".format(len(commands)))
    logging.info("Number of worker instances: {}.".format(num_workers))
    logging.debug("Starting simc with commands={}".format(commands))
    try:
        counter = 0
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


def _start_simulation(files_to_sim: List[str],
                      player_profile: Profile,
                      stage: int,
                      is_last_stage: bool,
                      target_error: Optional[float] = None,
                      iterations: Optional[int] = None):
    output_time = "{:%Y-%m-%d_%H-%M-%S}".format(datetime.datetime.now())
    # TODO: is this needed?
    files_to_sim = [f for f in files_to_sim if f.endswith('.simc')]

    num_files_to_sim = len(files_to_sim)
    if num_files_to_sim == 0:
        raise ValueError(
            "Number of files to sim in stage {} is 0. Check path (spaces? special chars?)"
            .format(stage))

    # First generate global simc options
    opts = SimcOptions(
        player_profile=player_profile,
        is_last_stage=is_last_stage,
        target_error=target_error,
        iterations=iterations,
    )
    sim_options = os.path.join(os.path.dirname(files_to_sim[0]),
                               'arguments.simc')
    with open(sim_options, 'w') as f:
        f.write(opts.sim_options)

    # Generate arguments for launching simc for each splitted file
    commands = []
    for file in files_to_sim:
        base_path, filename = os.path.split(file)
        basename, _extension = os.path.splitext(filename)
        result = os.path.join(base_path, f'b{basename}.result')

        cmd = [
            settings.simc_path,
            f'input={sim_options}',
            f'input={file}',
            f'output={result}',
        ]

        if num_files_to_sim == 1 or is_last_stage:
            html_file = os.path.join(base_path,
                                     f'{output_time}-{basename}.html')
            cmd.append(f'html={html_file}')

        commands.append(cmd)
    return _launch_simc_commands(commands, is_last_stage)


def simulate(subdir, player_profile: Profile, stage, is_last_stage, target_error: Optional[float] = None, iterations: Optional[int] = None):
    """Start the simulation process for a given stage/input"""
    logging.info("Starting simulation.")
    logging.debug("Started simulation with {}".format(locals()))
    files = os.listdir(subdir)
    files = [f for f in files if not f.endswith(".result")]
    files = [os.path.join(subdir, f) for f in files]

    start = datetime.datetime.now()
    result = _start_simulation(files_to_sim=files,
                               player_profile=player_profile,
                               stage=stage,
                               is_last_stage=is_last_stage,
                               target_error=target_error,
                               iterations=iterations)
    end = datetime.datetime.now()
    logging.info("Simulation took {}.".format(end - start))

    if is_last_stage:
        baseline = None
        for fn in files:
            with open(fn, 'r') as fd:
                for p in load_multiple_profiles(fd):
                    if baseline is None:
                        baseline = p
                    else:
                        logging.info(f'Diff between {baseline.profile_name} and {p.profile_name}:')
                        diff = baseline.baseline.diff(p.baseline)
                        if diff:
                            only_base, only_p = diff
                            logging.info(f'< {baseline.profile_name}: {only_base}')
                            logging.info(f'> {p.profile_name}: {only_p}')
                        if baseline.talents[0] != p.talents[0]:
                            logging.info(f'< {baseline.profile_name}: talents={baseline.talents[0]}')
                            logging.info(f'> {p.profile_name}: talents={p.talents[0]}')

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
            # if dps difference is less than sqrt(err_best**2+err**2), keep result
            if metric_best_player - metric < math.sqrt(
                    err ** 2 + metric_error_best_player ** 2) * settings.default_error_rate_multiplier / 1.96:
                output.append(entry)
    return output


def grab_best(filter_by, filter_criterium, source_subdir, target_subdir, origin, split_optimally=True):
    """
    Determine best simulations and grabs their profiles for further simming.
    """
    print("Grabbest:")
    print("Variables: filter by: " + str(filter_by))
    print("Variables: filter_criterium: " + str(filter_criterium))
    print("Variables: target_subdir: " + str(target_subdir))
    print("Variables: origin: " + str(origin))

    user_class = ""

    best = []
    print("Variables: source_subdir: " + str(source_subdir))
    files = os.listdir(source_subdir)
    files = [f for f in files if f.endswith(".result")]
    files = [os.path.join(source_subdir, f) for f in files]
    logging.debug("Grabbing files: {}".format(files))

    start = datetime.datetime.now()
    metric = settings.select_by_metric
    logging.info("Selecting by metric: '{}'.".format(metric))
    metric_regex = re.compile(f"\s*{metric}=(\d+\.\d+) {metric}-Error=(\d+\.\d+)/(\d+\.\d+)%", re.IGNORECASE)
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

    # Retain the baseline
    baseline = best[0]
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
    if baseline['name'] not in sortednames:
        sortednames.insert(0, baseline['name'])

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
        for profile in _parse_profiles_from_file(source, user_class):
            _classname, profilename = profile[0].split("=")
            profilename = profilename.strip('"')
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
