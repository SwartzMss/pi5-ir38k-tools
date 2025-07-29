#!/usr/bin/env python3
"""将 ``mode2`` 日志转换成 LIRC 配置文件（ENC 编码）。

本脚本仅支持 **NEC 协议** 的 ``mode2`` 输出，需使用 Python 3.10 及以上版本。

假设你按照按键顺序依次使用 ``mode2`` 录制，本脚本会自动将相同的 NEC 码归组并求
均值，因此无需手动指定每个按键的样本次数。

使用示例：

```bash
python tools/mode2_to_lirc.py --log xxx.log --key KEY_UP \
    --output myremote.conf --name myremote
```
"""

import argparse
import statistics
from pathlib import Path
from typing import Dict, List


THRESHOLD_GAP_US = 30000  # consider a space longer than this as key separator
BIT_THRESHOLD_US = 1000   # default logic-1 threshold, may be adapted

REPEAT_FRAME = -1  # special return for NEC repeat code


def parse_log(path: Path) -> List[List[int]]:
    """Parse mode2 log and return list of pulse/space sequences."""
    groups: List[List[int]] = []
    current: List[int] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            typ, value = line.split()
            value = int(value)
        except ValueError:
            continue
        if typ not in {"pulse", "space"}:
            continue
        # separator: long space
        if typ == "space" and value > THRESHOLD_GAP_US and current:
            groups.append(current)
            current = []
            continue
        current.append(value)
    if current:
        groups.append(current)
    return groups


def calibrate_nec(groups: List[List[int]]) -> dict:
    """Calculate dynamic thresholds from captured frames."""
    headers_pulse: List[int] = []
    headers_space: List[int] = []
    bit_spaces: List[int] = []
    for g in groups:
        if len(g) < 10:
            # short frame, likely repeat or noise
            continue
        headers_pulse.append(g[0])
        headers_space.append(g[1])
        for i in range(3, len(g), 2):
            bit_spaces.append(g[i])

    if not headers_pulse or not headers_space or not bit_spaces:
        return {
            "header_range": (8000, 10000),
            "space_range": (4000, 5000),
            "bit_threshold": BIT_THRESHOLD_US,
            "header_pulse": 9000,
            "header_space": 4500,
            "zero_space": 560,
            "one_space": 1690,
        }

    header_pulse_med = statistics.median(headers_pulse)
    header_space_med = statistics.median(headers_space)

    bit_spaces.sort()
    mid = len(bit_spaces) // 2
    zero_med = statistics.median(bit_spaces[:mid]) if mid > 0 else 560
    one_med = statistics.median(bit_spaces[mid:]) if mid > 0 else 1690
    bit_threshold = (zero_med + one_med) / 2

    return {
        "header_range": (header_pulse_med * 0.9, header_pulse_med * 1.1),
        "space_range": (header_space_med * 0.9, header_space_med * 1.1),
        "bit_threshold": bit_threshold,
        "header_pulse": header_pulse_med,
        "header_space": header_space_med,
        "zero_space": zero_med,
        "one_space": one_med,
    }


def decode_protocol_nec(
    pulses: List[int],
    head_range: tuple[float, float],
    space_range: tuple[float, float],
    bit_threshold: float,
    supported_lengths: set[int],
) -> int | None:
    """Decode a NEC infrared sequence into an integer code.

    Returns ``REPEAT_FRAME`` if a repeat code is detected.
    """
    if len(pulses) < 3:
        return None

    # repeat frame: 9ms + 2.25ms + 560us
    if 2000 <= pulses[1] <= 2500 and len(pulses) <= 4:
        return REPEAT_FRAME

    if not (head_range[0] <= pulses[0] <= head_range[1]):
        return None
    if not (space_range[0] <= pulses[1] <= space_range[1]):
        return None

    bits = []
    i = 2
    while i + 1 < len(pulses):
        pulse = pulses[i]
        space = pulses[i + 1]
        if pulse < 200:
            break
        bits.append(1 if space > bit_threshold else 0)
        i += 2

    if len(bits) not in supported_lengths:
        return None

    value = 0
    for b in bits:
        value = (value << 1) | b
    return value


def decode_protocol_rc5(pulses: List[int]) -> int | None:
    """Placeholder for RC5 protocol decoder."""
    return None


def decode_protocol_sony(pulses: List[int]) -> int | None:
    """Placeholder for Sony protocol decoder."""
    return None


def build_conf(
    codes: List[int],
    names: List[str],
    remote: str = "myremote",
    flags: str = "SPACE_ENC|CONST_LENGTH",
) -> str:
    """Create a minimal LIRC configuration in ENC (encoded) format."""
    lines = [
        "begin remote",
        f"  name  {remote}",
        f"  flags  {flags}",
        "  eps            30",
        "  aeps           100",
        f"  gap           {THRESHOLD_GAP_US}",
        "  frequency    38000",
        "",
        "  begin codes",
    ]
    for name, code in zip(names, codes):
        code_str = f"0x{code:X}"
        lines.append(f"    {name:16} {code_str}")
    lines.append("  end codes")
    lines.append("end remote")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 mode2 日志转换为 LIRC 的 ENC 格式配置文件")
    parser.add_argument(
        "--log",
        required=True,
        type=Path,
        help="mode2 输出的日志文件",
    )
    parser.add_argument(
        "--key",
        help="按键名称，默认为 KEY_1",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("remote.conf"),
        help="生成的 conf 文件路径",
    )
    parser.add_argument("--name", default="myremote", help="遥控器名称")
    parser.add_argument(
        "--flags",
        default="SPACE_ENC|CONST_LENGTH",
        help="LIRC remote flags",
    )
    parser.add_argument(
        "--bits",
        default="16,32",
        help="允许的位数，例如 32,40,48",
    )
    args = parser.parse_args()

    groups = parse_log(args.log)
    print(f"检测到 {len(groups)} 组数据")

    calib = calibrate_nec(groups)
    print(
        "动态阈值:",
        f"header {calib['header_range'][0]:.0f}-{calib['header_range'][1]:.0f} ",
        f"space {calib['space_range'][0]:.0f}-{calib['space_range'][1]:.0f} ",
        f"bit {calib['bit_threshold']:.0f}",
    )

    supported_lengths = {int(b) for b in args.bits.split(',') if b.strip()}

    codes_by_value: Dict[int, List[int]] = {}
    order: List[int] = []
    for grp in groups:
        code = decode_protocol_nec(
            grp,
            calib["header_range"],
            calib["space_range"],
            calib["bit_threshold"],
            supported_lengths,
        )
        if code == REPEAT_FRAME:
            print("提示：检测到重复帧，已忽略")
            continue
        if code is None:
            print("警告：有一组数据解码失败，已跳过")
            continue
        if code not in codes_by_value:
            codes_by_value[code] = []
            order.append(code)
        codes_by_value[code].append(code)

    if not order:
        parser.error("未解析出任何有效 NEC 码，退出")

    if len(order) > 1:
        parser.error("仅支持一次解析单个按键，请确认日志内容")

    key_name = args.key if args.key else "KEY_1"

    codes: List[int] = [round(statistics.fmean(codes_by_value[order[0]]))]
    key_names = [key_name]

    conf = build_conf(codes, key_names, args.name, args.flags)
    args.output.write_text(conf)
    print(f"已写入 {args.output}")

    print("SPACE_ENC 参数参考：")
    print(f"  header_pulse = {int(calib['header_pulse'])}")
    print(f"  header_space = {int(calib['header_space'])}")
    print(f"  zero_space   = {int(calib['zero_space'])}")
    print(f"  one_space    = {int(calib['one_space'])}")
    print(f"  gap          = {THRESHOLD_GAP_US}")


if __name__ == "__main__":
    main()
