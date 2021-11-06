import serial
import threading
import queue
from usb_dmx.dataclasses import DummyQueue


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
