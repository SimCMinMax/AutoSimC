from collections import defaultdict
import itertools
import json
import os.path
from typing import Dict, List, Tuple
import warnings

from settings import settings
try:
    from settings_local import settings
except ImportError:
    pass

# dict of [class][spec] => to full name as appears in Analysis.json
_CLASS_SPECS = {
    'deathknight': {
        'frost': 'Frost Death Knight',
        'unholy': 'Unholy Death Knight',
        'blood': 'Blood Death Knight',
    },
    'demonhunter': {
        'havoc': 'Havoc Demon Hunter',
        'vengance': 'Vengance Demon Hunter',
    },
    'druid': {
        'balance': 'Balance Druid',
        'feral': 'Feral Druid',
        'guardian': 'Guardian Druid',
        'restoration': 'Restoration Druid',
    },
    'hunter': {
        'beast_mastery': 'Beast Mastery Hunter',
        'marksmanship': 'Marksmanship Hunter',
        'survival': 'Survival Hunter',
    },
    'mage': {
        'arcane': 'Arcane Mage',
        'fire': 'Fire Mage',
        'frost': 'Frost Mage',
    },
    'paladin': {
        'holy': 'Holy Paladin',
        'protection': 'Protection Paladin',
        'retribution': 'Retribution Paladin',
    },
    'priest': {
        'discipline': 'Discipline Priest',
        'holy': 'Holy Priest',
        'shadow': 'Shadow Priest',
    },
    'monk': {
        'brewmaster': 'Brewmaster Monk',
        'mistweaver': 'Mistweaver Monk',
        'windwalker': 'Windwalker Monk',
    },
    'rogue': {
        'assassination': 'Assassination Rogue',
        'outlaw': 'Outlaw Rogue',
        'subtlety': 'Subtlety Rogue',
    },
    'shaman': {
        'elemental': 'Elemental Shaman',
        'enhancement': 'Enhancement Shaman',
        'restoration': 'Restoration Shaman',
    },
    'warlock': {
        'affliction': 'Affliction Warlock',
        'demonology': 'Demonology Warlock',
        'destruction': 'Destruction Warlock',
    },
    'warrior': {
        'arms': 'Arms Warrior',
        'fury': 'Fury Warrior',
        'protection': 'Protection Warrior',
    },
}

# Healer Specializations
HEALERS = frozenset({
    'Restoration Druid',
    'Discipline Priest',
    'Holy Priest',
    'Holy Paladin',
    'Mistweaver Monk',
    'Restoration Shaman',
})

# Tank specializations
TANKS = frozenset({
    'Blood Death Knight',
    'Vengeance Demon Hunter',
    'Guardian Druid',
    'Protection Paladin',
    'Brewmaster Monk',
    'Protection Warrior',
})

ALL_CLASSES = frozenset(_CLASS_SPECS.keys())

_ALL_SPECS = list(itertools.chain(*(s.values()
                                    for s in _CLASS_SPECS.values())))


def getClassSpec(c_class: str, c_spec: str):
    """Gets the full name of a simc character class and specialization."""
    try:
        class_spec = _CLASS_SPECS[c_class][c_spec]
    except KeyError:
        raise ValueError(
            f'Unsupported class/spec-combination: {c_class} - {c_spec}')

    if class_spec in HEALERS or class_spec in TANKS:
        warnings.warn(
            'You are trying to use a tank or heal-spec! Be aware that this may lead to no or incomplete '
            'results!\n You may need to generate a new Analyzer.json using Analyzer.py which includes a '
            'profile with your spec.')
    return class_spec


def getRole(c_class: str, c_spec: str) -> str:
    if c_class in ('deathknight', 'warrior'):
        return 'strattack'
    elif c_class in ('demonhunter', 'hunter', 'rogue'):
        return 'agiattack'
    elif c_class in ('mage', 'priest', 'warlock'):
        return 'spell'
    elif c_class == 'druid':
        if c_spec in ('balance', 'restoration'):
            return 'spell'
        elif c_spec in ('feral', 'guardian'):
            return 'agiattack'
    elif c_class == 'paladin':
        if c_spec in ('protection', 'retribution'):
            return 'strattack'
        elif c_spec == 'holy':
            return 'spell'
    elif c_class == 'monk':
        if c_spec in ('brewmaster', 'windwalker'):
            return 'agiattack'
        elif c_spec == 'mistweaver':
            return 'spell'
    elif c_class == 'shaman':
        if c_spec == 'enhancement':
            return 'agiattack'
        elif c_spec  in ('elemental', 'restoration'):
            return 'spell'
    raise ValueError(f'Unknown role for {c_class}/{c_spec}')



def _read_analyzer_data() -> Dict[str, Tuple[float, int, float]]:
    """Reads spec simulation data from profiles/Analysis.json"""
    specs = defaultdict(list)
    filename = os.path.join(os.path.dirname(__file__), settings.analyzer_path,
                            settings.analyzer_filename)
    with open(filename, 'r') as f:
        for variant in json.load(f)[0]:
            for p in variant['playerdata']:
                if p['specialization'] not in _ALL_SPECS:
                    raise ValueError(
                        f'Unhandled class/spec in {filename}: {p["specialization"]}'
                    )
                if p['specialization'] not in specs:
                    specs[p['specialization']] = []
                for s in p['specdata']:
                    specs[p['specialization']].append((
                        float(variant['target_error']),
                        int(s['iterations']),
                        float(s['elapsed_time_seconds']),
                    ))
    return specs


_ANALYZER_DATA = _read_analyzer_data()


def get_analyzer_data(class_spec: str) -> List[Tuple[float, int, float]]:
    """
    Get precomputed analysis data (target_error, iterations, elapsed_time_seconds) for a given class_spec
    """
    return _ANALYZER_DATA.get(class_spec, [])
