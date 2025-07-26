"""Wait for an infrared signal via the LIRC device."""

import argparse
from ir_device import record_pulses


def main() -> None:
    parser = argparse.ArgumentParser(description="wait for IR signal")
    parser.add_argument("--device", default="/dev/lirc0", help="LIRC device path")
    parser.add_argument("--timeout", type=float, default=5.0, help="wait time in seconds")
    args = parser.parse_args()

    pulses = record_pulses(args.device, args.timeout)
    if pulses:
        print("IR signal detected")
    else:
        print("no signal")


if __name__ == "__main__":
    main()

