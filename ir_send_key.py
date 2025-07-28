#!/usr/bin/env python3
"""Send a configured LIRC key via the transmit device."""

import argparse
import time
import lirc


def main() -> None:
    parser = argparse.ArgumentParser(description="send a LIRC key code")
    parser.add_argument("remote", help="remote name defined in lircd.conf")
    parser.add_argument("key", help="key name to send")
    parser.add_argument(
        "--lircd", default="/var/run/lirc/lircd", help="path to lircd socket"
    )
    parser.add_argument(
        "--device", default="/dev/lirc1", help="LIRC transmit device"
    )
    parser.add_argument(
        "--count", type=int, default=1, help="times to send the key"
    )
    parser.add_argument(
        "--delay", type=float, default=0.0, help="delay between repeats in seconds"
    )
    args = parser.parse_args()

    for i in range(args.count):
        lirc.send_once(args.remote, [args.key], lircd=args.lircd, device=args.device)
        if i < args.count - 1 and args.delay > 0:
            time.sleep(args.delay)


if __name__ == "__main__":
    main()
