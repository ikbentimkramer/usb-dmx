from typing import Tuple, Any
from itertools import cycle


class BPM(int):
    MIN_BPM = 30

    # min BPM of 30 to make sure the clock does not take ages to
    # complete.

    MAX_BPM = 2400

    # max refresh rate of DMX is 44Hz, so to be safe we
    # use 40Hz * 60s = 2400 bpm as max

    def __new__(cls, value: int) -> 'BPM':
        if (cls.MIN_BPM <= value <= cls.MAX_BPM):
            return super(BPM, cls).__new__(cls, value)
        else:
            raise (ValueError(
                f'BPM should be between {cls.MIN_BPM} and {cls.MAX_BPM}'))

    def __repr__(self) -> str:
        return f'BPM({int(self)})'


class RGB(bytes):
    def __new__(cls, value: str) -> 'RGB':
        if (len(value) != 6):
            raise (ValueError(
                f'length of provided value "{value}" to RGB() is '
                f'{len(value)} instead of 6'))
        return super(RGB, cls).__new__(cls, bytes.fromhex(value))

    def __repr__(self) -> str:
        return f'RGB(#{self.hex()})'


class Scene(bytearray):
    CHANNELS = 512

    def __init__(self, *args: Tuple[int, RGB]) -> None:
        super().__init__(self.CHANNELS)
        for (channel, color) in args:
            upper_bound = channel + len(color)
            if (upper_bound <= self.CHANNELS):
                self[channel:upper_bound] = color
            else:
                raise ValueError(f'color requires {len(color)} channels,'
                                 f' but only {self.CHANNELS - channel}'
                                 f' channels available.')


class Chase:
    def __init__(self, *args: Scene) -> None:
        self.gen = cycle(args)

    def __iter__(self) -> 'Chase':
        return self

    def __next__(self) -> Scene:
        return next(self.gen)


class DummyQueue:
    """Queue that does nothing

This class implements (a part of) the queue.Queue API, but its calls
do not do anything. This class should be used for testing purposes
only."""
    def put(*args: Any, **kwargs: Any) -> None:
        pass

    def put_nowait(*args: Any, **kwargs: Any) -> None:
        pass

    def get(*args: Any, **kwargs: Any) -> None:
        pass

    def get_nowait(*args: Any, **knwargs: Any) -> None:
        pass
