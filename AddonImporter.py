import logging

from profile import Profile

def build_profile_simc_addon(args) -> Profile:
    player_profile = Profile()

    # no sections available, so parse each line individually
    input_encoding = 'utf-8'
    try:
        with open(args.inputfile, "r", encoding=input_encoding) as f:
            player_profile.load_simc(f)

    except UnicodeDecodeError as e:
        raise RuntimeError("""AutoSimC could not decode your input file '{file}' with encoding '{enc}'.
        Please make sure that your text editor encodes the file as '{enc}',
        or as a quick fix remove any special characters from your character name.""".format(file=args.inputfile,
                                                                                            enc=input_encoding)) from e

    # Build 'general' profile options which do not permutate once into a simc-string
    logging.info(f'SimC options: {player_profile}')
    logging.debug(f'Built simc general options string: {player_profile.general_options}')
    return player_profile
