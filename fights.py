from dataclasses import dataclass
from typing import Dict, Iterator, Optional, Sequence

from i18n import _

_FIGHTS = {}  # type: Dict[str, 'Fight']


@dataclass(frozen=True)
class Fight:
    name: str
    description: str
    # fight_style=
    style: Optional[str] = None
    # custom fights expressed as simc config
    custom: Optional[Sequence[str]] = None

    def __post_init__(self):
        if (self.style is None and self.custom is None) or (
                self.style is None == self.custom is None):
            raise ValueError(f'Fight {self.name} must have exactly one of '
                             '"style" or "custom" set')
        _FIGHTS[self.name.lower()] = self

    @property
    def simc_options(self) -> Sequence[str]:
        if self.style:
            return (f'fight_style={self.style}', )
        else:
            return self.custom


def all_fights():
    return _FIGHTS.values()


def get_fight(name: str) -> Optional[Fight]:
    return _FIGHTS.get(name.lower())


# Fights supported by SimC
# https://github.com/simulationcraft/simc/blob/e6856b149d75536ddcad09dcb88039f00266f288/qt/sc_OptionsTab.cpp#L984
Fight(
    name='Patchwerk',
    style='Patchwerk',
    description=_('Tank-n-spank'),
)
Fight(
    name='DungeonSlice',
    style='DungeonSlice',
    description=_('Multi-segment simulation meant to approximate M+ dungeon and boss pulls'),
)
Fight(
    name='LightMovement',
    style='LightMovement',
    description=_('Fight with infrequent movement'),
)
Fight(
    name='HeavyMovement',
    style='HeavyMovement',
    description=_('Fight with frequent movement'),
)
Fight(
    name='HelterSkelter',
    style='HelterSkelter',
    description=_('Movement, Stuns, Interrupts, Target-Switching (every 2min)'),
)
Fight(
    name='HecticAddCleave',
    style='HecticAddCleave',
    description=_('Heavy Movement, Frequent Add Spawns'),
)
Fight(
    name='Ultraxion',
    style='Ultraxion',
    description=_('Periodic Stuns, Raid Damage'),
)
Fight(
    name='Beastlord',
    style='Beastlord',
    description=_('Random Movement, Advanced Positioning, Frequent Single and Wave Add Spawns'),
)
Fight(
    name='CastingPatchwerk',
    style='CastingPatchwerk',
    description=_('Tank-N-Spank; Boss considered always casting (to test interrupt procs on cooldown)'),
)

# AutoSimC custom fights, define your own here.
Fight(
    name='Two Patchwerks, stacked',
    custom=('enemy=Patchwerk', 'enemy=Patchwerk2'),
    description=_('Two Patchwerks, standing on top of each other'),
)
Fight(
    name='Two Patchwerks, 27 yards away from each other',
    custom=(
        'enemy=Patchwerk',
        'enemy=Patchwerk2',
        'raid_events+=/move_enemy,enemy_name=Patchwerk2,cooldown=2000,duration=1000,x=-27,y=0',
    ),
    description=_('Two Patchwerks, which are standing far away'),
)
