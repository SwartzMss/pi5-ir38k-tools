"""LIRC infrared utilities using the kernel gpio-ir driver."""

from __future__ import annotations

import array
import fcntl
import os
import struct
import time
from typing import Iterable

# IOCTL constants calculated from linux/lirc.h
LIRC_MODE_PULSE = 0x00000002
LIRC_SET_SEND_MODE = 0x40046911
LIRC_SET_REC_MODE = 0x40046912
LIRC_SET_SEND_CARRIER = 0x40046913
LIRC_SET_SEND_DUTY_CYCLE = 0x40046915
LIRC_SET_REC_TIMEOUT = 0x40046918
LIRC_SET_REC_TIMEOUT_REPORTS = 0x40046919


def record_pulses(device: str = "/dev/lirc0", timeout: float = 2.0) -> list[int]:
    """Record raw pulses from ``device`` for up to ``timeout`` seconds."""
    pulses: list[int] = []
    with open(device, "rb", buffering=0) as f:
        fcntl.ioctl(f, LIRC_SET_REC_MODE, LIRC_MODE_PULSE)
        fcntl.ioctl(f, LIRC_SET_REC_TIMEOUT, int(timeout * 1_000_000))
        fcntl.ioctl(f, LIRC_SET_REC_TIMEOUT_REPORTS, 1)
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            data = f.read(4)
            if not data:
                break
            pulses.append(struct.unpack("I", data)[0])
    return pulses


def send_pulses(
    pulses: Iterable[int],
    device: str = "/dev/lirc0",
    freq: int = 38000,
    duty_cycle: float = 0.33,
) -> None:
    """Send ``pulses`` using ``device`` with given frequency and duty cycle."""
    with open(device, "wb", buffering=0) as f:
        fcntl.ioctl(f, LIRC_SET_SEND_MODE, LIRC_MODE_PULSE)
        fcntl.ioctl(f, LIRC_SET_SEND_CARRIER, freq)
        duty = int(duty_cycle * 100)
        fcntl.ioctl(f, LIRC_SET_SEND_DUTY_CYCLE, duty)
        arr = array.array("I", pulses)
        os.write(f.fileno(), arr.tobytes())

