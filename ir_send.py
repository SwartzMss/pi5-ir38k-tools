"""Send a single infrared pulse for testing."""

import argparse
from ir_device import send_pulses


def main() -> None:
    parser = argparse.ArgumentParser(description="send test pulse")
    parser.add_argument("--device", default="/dev/lirc0", help="LIRC device path")
    parser.add_argument("--duration", type=float, default=0.5, help="pulse duration in seconds")
    parser.add_argument("--freq", type=int, default=38000, help="carrier frequency")
    args = parser.parse_args()

    send_pulses([int(args.duration * 1_000_000)], args.device, args.freq)


if __name__ == "__main__":
    main()

