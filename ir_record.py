"""Record infrared pulses via the LIRC device."""

import argparse
from ir_device import record_pulses


def main() -> None:
    parser = argparse.ArgumentParser(description="record IR pulses")
    parser.add_argument("--device", default="/dev/lirc0", help="LIRC device path")
    parser.add_argument("--timeout", type=float, default=2.0, help="record time in seconds")
    args = parser.parse_args()

    pulses = record_pulses(args.device, args.timeout)
    if pulses:
        print(",".join(str(p) for p in pulses))
    else:
        print("no signal captured")


if __name__ == "__main__":
    main()

