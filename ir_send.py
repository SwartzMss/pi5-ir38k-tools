"""示例代码：在 Raspberry Pi 5 上发送 38kHz 红外信号。"""

import time
import argparse
import lgpio

DEFAULT_PIN = 18  # 默认红外 LED 所在的 GPIO

def send_pulse(handle, pin, duration=0.5, freq=38000, duty_cycle=0.5):
    """发送指定持续时间的 38kHz 红外载波信号。"""
    duty = int(duty_cycle * 1_000_000)  # 占空比分子, 范围 0-1_000_000
    lgpio.tx_pwm(handle, pin, freq, duty)
    time.sleep(duration)
    lgpio.tx_pwm(handle, pin, 0, 0)

def main():
    parser = argparse.ArgumentParser(description="发送 38kHz 红外信号")
    parser.add_argument(
        "--pin",
        type=int,
        default=DEFAULT_PIN,
        help="用于发射的 GPIO (默认: %(default)s)",
    )
    args = parser.parse_args()

    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_output(h, args.pin)
    try:
        print("发送 38kHz 脉冲...")
        send_pulse(h, args.pin)
    finally:
        lgpio.gpiochip_close(h)

if __name__ == "__main__":
    main()
