"""示例代码：在 Raspberry Pi 5 上接收红外信号。"""

import argparse

from ir_device import IRReceiver

DEFAULT_PIN = 23  # 默认红外接收头所在的 GPIO


def main():
    parser = argparse.ArgumentParser(description="接收红外信号")
    parser.add_argument(
        "--pin",
        type=int,
        default=DEFAULT_PIN,
        help="用于接收的 GPIO (默认: %(default)s)",
    )
    args = parser.parse_args()

    receiver = IRReceiver(args.pin)
    try:
        print("等待信号...")
        if receiver.wait():
            print("检测到红外信号")
        else:
            print("未检测到红外信号")
    finally:
        receiver.close()


if __name__ == "__main__":
    main()
