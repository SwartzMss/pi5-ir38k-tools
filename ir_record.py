"""记录红外遥控器的脉冲序列。"""

import argparse

from ir_device import IRReceiver

DEFAULT_PIN = 23  # 默认红外接收头的 GPIO


def record_ir(pin: int, timeout: float = 2.0):
    """在给定时间内记录引脚电平变化, 返回微秒为单位的脉冲时长列表。"""
    receiver = IRReceiver(pin)
    try:
        pulses = receiver.record(timeout)
        return pulses
    finally:
        receiver.close()


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
