"""示例代码：在 Raspberry Pi 5 上接收红外信号。"""

import time
import argparse
import lgpio

DEFAULT_PIN = 23  # 默认红外接收头所在的 GPIO


def wait_signal(handle, pin, timeout=5):
    """等待红外信号，超时时间单位为秒。"""
    start = time.time()
    while time.time() - start < timeout:
        if lgpio.gpio_read(handle, pin):
            print("检测到红外信号")
            return True
        time.sleep(0.01)
    print("未检测到红外信号")
    return False


def main():
    parser = argparse.ArgumentParser(description="接收红外信号")
    parser.add_argument(
        "--pin",
        type=int,
        default=DEFAULT_PIN,
        help="用于接收的 GPIO (默认: %(default)s)",
    )
    args = parser.parse_args()

    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_input(h, args.pin)
    try:
        print("等待信号...")
        wait_signal(h, args.pin)
    finally:
        lgpio.gpiochip_close(h)


if __name__ == "__main__":
    main()
