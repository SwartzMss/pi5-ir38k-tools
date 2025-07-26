"""Replay infrared pulses via the LIRC device."""

import argparse
from ir_device import send_pulses


def main() -> None:
    parser = argparse.ArgumentParser(description="play back IR pulses")
    parser.add_argument("codes", help="comma separated pulse durations")
    parser.add_argument("--device", default="/dev/lirc0", help="LIRC device path")
    parser.add_argument("--freq", type=int, default=38000, help="carrier frequency")
    parser.add_argument("--duty", type=float, default=0.33, help="duty cycle (0-1)")
    args = parser.parse_args()

    if args.codes.startswith("@"):  # read from file
        with open(args.codes[1:], "r") as fh:
            codes_str = fh.read().strip()
    else:
        codes_str = args.codes
    pulses = [int(x) for x in codes_str.split(',') if x]
    send_pulses(pulses, args.device, args.freq, args.duty)


if __name__ == "__main__":
    main()

