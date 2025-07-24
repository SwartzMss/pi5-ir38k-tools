"""记录红外遥控器的脉冲序列。"""

import argparse
import time

import lgpio

DEFAULT_PIN = 23  # 默认红外接收头的 GPIO


def record_ir(pin: int, timeout: float = 2.0):
    """在给定时间内记录引脚电平变化, 返回微秒为单位的脉冲时长列表。"""
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_input(h, pin)

    pulses = []
    level = lgpio.gpio_read(h, pin)
    last = time.perf_counter()
    end_time = last + timeout

    try:
        while time.perf_counter() < end_time:
            if lgpio.gpio_read(h, pin) != level:
                now = time.perf_counter()
                pulses.append(int((now - last) * 1_000_000))
                last = now
                level ^= 1
        return pulses
    finally:
        lgpio.gpiochip_close(h)


def main():
    parser = argparse.ArgumentParser(description="记录红外脉冲序列")
    parser.add_argument("--pin", type=int, default=DEFAULT_PIN, help="接收红外的GPIO")
    parser.add_argument("--timeout", type=float, default=2.0, help="记录时长(秒)")
    args = parser.parse_args()

    print("请对准接收器按下遥控器按键...")
    pulses = record_ir(args.pin, args.timeout)
    if pulses:
        print(",".join(str(p) for p in pulses))
    else:
        print("未检测到信号")


if __name__ == "__main__":
    main()
