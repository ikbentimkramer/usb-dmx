import serial
import threading
import queue
import time
from usb_dmx.dataclasses import BPM, Chase, DummyQueue


class DMXConnection(threading.Thread):
    # DMX protocol settings
    BAUDRATE = 250000
    BYTESIZE = serial.EIGHTBITS
    PARITY = serial.PARITY_NONE
    STOPBITS = serial.STOPBITS_TWO
    STARTCODE = b'\x00'
    BREAK_LEN = 0.000068  # In seconds.
    MARK_AFTER_BREAK = b'\x01'

    # BREAK_LEN and the leading zeroes of MARK_AFTER_BREAK should add
    # up to 100 microseconds. A bit takes 4 microseconds to send and a
    # frame (like MARK_AFTER_BREAK) starts with a leading zero.

    def __init__(self, port: str, data_queue: queue.Queue[bytes]) -> None:
        super().__init__(daemon=True)
        if port.startswith('loop://'):  # used for testing
            self.connection = serial.serial_for_url(port)
            self.connection.baudrate = self.BAUDRATE
            self.connection.bytesize = self.BYTESIZE
            self.connection.parity = self.PARITY
            self.connection.stopbits = self.STOPBITS
            self.connection.queue = DummyQueue()
        else:
            self.connection = serial.Serial(port=port,
                                            baudrate=self.BAUDRATE,
                                            bytesize=self.BYTESIZE,
                                            parity=self.PARITY,
                                            stopbits=self.STOPBITS)
        self.data_queue = data_queue
        self.terminated = threading.Event()
        self.timeout = 0.5
        self.name = 'DMXConnection'

    def run(self) -> None:
        data = b'\x00' * 512
        while not self.terminated.is_set():
            try:
                data = self.data_queue.get(True, self.timeout)
            except queue.Empty:
                pass
            finally:
                # Construct and send a DMX packet. A DMX packet
                # consists at least of a break, mark after break,
                # startcode and data. The data may be up to 512 bytes.
                self.connection.send_break(self.BREAK_LEN)
                self.connection.write(self.MARK_AFTER_BREAK + self.STARTCODE)
                self.connection.write(data)
                self.connection.flush()


class Clock(threading.Thread):
    def __init__(self, bpm: BPM) -> None:
        super().__init__(daemon=True)
        self.bpm = bpm
        self.pulse = threading.Event()
        self.terminated = threading.Event()
        self.name = 'Clock'

    def run(self) -> None:
        while not self.terminated.is_set():
            time.sleep(60 / self.bpm)
            self.pulse.set()
            self.pulse.clear()


class DataProducer(threading.Thread):
    def __init__(self, port: str, default_gen: Chase,
                 bpm: BPM = BPM(120)) -> None:
        super().__init__(daemon=True)
        self.clock = Clock(bpm)
        self.data_queue: queue.Queue = queue.Queue(2)
        self.gen_queue: queue.Queue = queue.Queue(2)
        self.gen_queue.put(default_gen)
        self.dmx = DMXConnection(port, self.data_queue)
        self.terminated = threading.Event()
        self.clock_timeout = 5
        self.dmx_timeout = 1
        self.name = 'Producer'

    def run(self) -> None:
        self.clock.start()
        self.dmx.start()
        gen = self.gen_queue.get_nowait()
        while not self.terminated.is_set():
            self.clock.pulse.wait(self.clock_timeout)
            try:
                gen = self.gen_queue.get_nowait()
            except queue.Empty:
                pass
            self.data_queue.put(next(gen), True, self.dmx_timeout)
        self.clock.terminated.set()
        self.dmx.terminated.set()
