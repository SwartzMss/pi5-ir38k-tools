"""示例代码：在 Raspberry Pi 5 上发送 38kHz 红外信号。"""

import argparse

from ir_device import IRSender

DEFAULT_PIN = 18  # 默认红外 LED 所在的 GPIO

def main():
    parser = argparse.ArgumentParser(description="发送 38kHz 红外信号")
    parser.add_argument(
        "--pin",
        type=int,
        default=DEFAULT_PIN,
        help="用于发射的 GPIO (默认: %(default)s)",
    )
    args = parser.parse_args()

    sender = IRSender(args.pin)
    try:
        print("发送 38kHz 脉冲...")
        sender.send_pulse()
    finally:
        sender.close()

if __name__ == "__main__":
    main()
