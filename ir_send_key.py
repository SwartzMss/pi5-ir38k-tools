#!/usr/bin/env python3
"""Send a configured LIRC key via the transmit device."""

import argparse
import os
import sys
import time
import lirc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="\u901a\u8fc7 LIRC \u7801\u8868\u53d1\u5c04\u7ea2\u591a\u6309\u952e"
    )
    parser.add_argument("--remote", required=True, help="\u9065\u63a7\u5668\u540d")
    parser.add_argument("--key", required=True, help="\u6309\u952e\u540d")
    parser.add_argument(
        "--lircd", default="/var/run/lirc/lircd", help="path to lircd socket"
    )
    parser.add_argument(
        "--device", default="/dev/lirc1", help="LIRC \u53d1\u5c04\u8bbe\u5907"
    )
    parser.add_argument("--count", type=int, default=1, help="\u53d1\u5c04\u6b21\u6570")
    parser.add_argument(
        "--delay", type=float, default=0.5, help="\u8fde\u53d1\u95f4\u9694\uff08\u79d2\uff09"
    )
    args = parser.parse_args()

    if not os.path.exists(args.device):
        print(f"\u8bbe\u5907 {args.device} \u4e0d\u5b58\u5728\uff0c\u8bf7\u68c0\u67e5 overlay \u914d\u7f6e\u548c\u786c\u4ef6\u8fde\u63a5！")
        sys.exit(1)

    try:
        for i in range(args.count):
            print(f"[{i+1}/{args.count}] \u53d1\u5c04 {args.remote} \u7684 {args.key} ...")
            lirc.send_once(args.remote, [args.key], lircd=args.lircd, device=args.device)
            if i < args.count - 1 and args.delay > 0:
                time.sleep(args.delay)
        print("\u5168\u90e8\u53d1\u5c04\u5b8c\u6210\u3002")
    except Exception as e:
        print("\u53d1\u5c04\u5931\u8d25:", e)
        print("\u53ef\u80fd\u539f\u56e0\uff1a\u7801\u8868\u672a\u52a0\u8f7d\u3001\u670d\u52a1\u672a\u91cd\u542f\u3001\u540d\u79f0\u62fc\u5199\u9519\u8bef\u3001\u786c\u4ef6\u672a\u63a5\u597d\u3002")


if __name__ == "__main__":
    main()
