"""Infrared device utilities with class-based interfaces."""

from typing import Iterable

import lgpio
import time


class IRDevice:
    """Base class handling open/close of a GPIO pin."""

    def __init__(self, pin: int, direction: str):
        self.pin = pin
        self.handle = lgpio.gpiochip_open(0)
        if direction == "in":
            lgpio.gpio_claim_input(self.handle, pin)
        else:
            lgpio.gpio_claim_output(self.handle, pin)
        self.direction = direction

    def close(self) -> None:
        lgpio.gpiochip_close(self.handle)


class IRSender(IRDevice):
    """Send infrared signals on a given GPIO pin."""

    def __init__(self, pin: int):
        super().__init__(pin, "out")

    def send_pulse(self, duration: float = 0.5, freq: int = 38000, duty_cycle: float = 0.5) -> None:
        duty = int(duty_cycle * 1_000_000)
        lgpio.tx_pwm(self.handle, self.pin, freq, duty)
        time.sleep(duration)
        lgpio.tx_pwm(self.handle, self.pin, 0, 0)

    def play(self, pulses: Iterable[int], freq: int = 38000) -> None:
        level = False
        for us in pulses:
            if level:
                lgpio.tx_pwm(self.handle, self.pin, freq, 500000)
            else:
                lgpio.tx_pwm(self.handle, self.pin, 0, 0)
            time.sleep(us / 1_000_000)
            level = not level
        lgpio.tx_pwm(self.handle, self.pin, 0, 0)


class IRReceiver(IRDevice):
    """Receive infrared signals from a given GPIO pin."""

    def __init__(self, pin: int):
        super().__init__(pin, "in")

    def wait(self, timeout: float = 5.0) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            if lgpio.gpio_read(self.handle, self.pin):
                return True
            time.sleep(0.01)
        return False

    def record(self, timeout: float = 2.0) -> list[int]:
        pulses: list[int] = []
        level = lgpio.gpio_read(self.handle, self.pin)
        last = time.perf_counter()
        end_time = last + timeout
        while time.perf_counter() < end_time:
            if lgpio.gpio_read(self.handle, self.pin) != level:
                now = time.perf_counter()
                pulses.append(int((now - last) * 1_000_000))
                last = now
                level ^= 1
        return pulses
