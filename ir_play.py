"""播放记录的红外脉冲序列。"""

import argparse

from ir_device import IRSender

DEFAULT_PIN = 18  # 默认红外发射 GPIO


def play_ir(pin: int, pulses, freq: int = 38000):
    """根据脉冲序列在指定引脚发送红外信号。"""
    sender = IRSender(pin)
    try:
        sender.play(pulses, freq)
    finally:
        sender.close()


def main():
    parser = argparse.ArgumentParser(description="播放红外脉冲序列")
    parser.add_argument("codes", help="逗号分隔的脉冲时长(微秒)")
    parser.add_argument("--pin", type=int, default=DEFAULT_PIN, help="发射红外的GPIO")
    parser.add_argument("--freq", type=int, default=38000, help="载波频率")
    args = parser.parse_args()

    pulses = [int(x) for x in args.codes.split(',') if x]
    play_ir(args.pin, pulses, args.freq)


if __name__ == "__main__":
    main()
