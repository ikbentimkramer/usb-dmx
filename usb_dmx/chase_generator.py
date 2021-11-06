import random
from typing import Any, List
from usb_dmx.dataclasses import RGB, Scene, Chase


class ChaseGenerator:

    # -- Color aliases --

    color_aliases = {
        'red': 'ff0000',
        'green': '00ff00',
        'blue': '0000ff',
        'yellow': 'ffff00',
        'magenta': 'ff00ff',
        'cyan': '00ffff',
        'orange': 'ff7f00',
        'pink': 'ff007f',
        'lime': '7fff00',
        'turquoise': '00ff7f',
        'purple': '7f00ff',
        'sky': '007fff',
        'white': 'ffffff',
        'black': '000000'
    }

    def color_from_alias(self, value: str) -> RGB:
        res = ''
        try:
            res = self.color_aliases[value]
        except KeyError:
            if value[0] == '#':
                res = value[1:]
            else:
                raise (ValueError(f'unknown color "{value}"'))
        return RGB(res)

    # -- General methods --

    def make_chase(self, config: dict) -> Chase:
        """Construct a Chase from a config dict input"""
        # this is an obtuse incantation, but I do not think a loop would
        # make it more clear
        return Chase(*[
            Scene(*[(channel, self.color_from_alias(color))
                    for channel, color in zip(config['channels'], scene)])
            for scene in config['scenes']
        ])

    # -- Constructor --

    def __init__(self, channels: List[int] = [0, 8]) -> None:
        self.channels = channels  # The first rgb channel of each lamp

    # -- Generators --

    def gen_random(self, scenes: int, *args: Any, **kwargs: Any) -> Chase:
        """Generate a random chase"""
        res: dict  # necessary for mypy (static typing)
        res = {'channels': self.channels}
        res['scenes'] = [
            random.choices(list(self.color_aliases.keys()),
                           k=len(self.channels)) for _ in range(scenes)
        ]
        return self.make_chase(res)

    def gen_iso(self,
                color1: str,
                color2: str = '#000000',
                *args: Any,
                **kwargs: Any) -> Chase:
        """Generate a chase with all lamps switching between two colors"""
        return self.make_chase({
            'channels':
            self.channels,
            'scenes': [[color1] * len(self.channels),
                       [color2] * len(self.channels)]
        })

    def gen_blackout(self, *args: Any, **kwargs: Any) -> Chase:
        """Turn all lamps off"""
        return self.make_chase({'channels': [0], 'scenes': [['#000000']]})

    def gen_mayday(self, *args: Any, **kwargs: Any) -> Chase:
        """Chase with two lamps alternating yellow and blue"""
        return self.make_chase({
            'channels':
            self.channels[0:2],
            'scenes': [['blue', 'yellow'], ['yellow', 'blue']]
        })

    def gen_colorwheel(self, *args: Any, **kwargs: Any) -> Chase:
        """Chase with two lamps rotating through a colorwheel"""
        return self.make_chase({
            'channels':
            self.channels[0:2],
            'scenes': [['red', 'orange'], ['orange', 'yellow'],
                       ['yellow', 'lime'], ['lime', 'green'],
                       ['green', 'turquoise'], ['turquoise', 'cyan'],
                       ['cyan', 'sky'], ['sky', 'blue'], ['blue', 'purple'],
                       ['purple', 'magenta'], ['magenta', 'pink'],
                       ['pink', 'red']]
        })
