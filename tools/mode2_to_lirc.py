#!/usr/bin/env python3
"""将 ``mode2`` 日志转换成 LIRC 配置文件。

默认会按 **NEC 协议** 解码生成 ENC 格式配置，也可通过 ``--proto raw``
直接输出 ``RAW_CODES`` 形式的脉冲数据。需使用 Python 3.10 及以上版本。

假设你按照按键顺序依次使用 ``mode2`` 录制，选择 ``nec`` 协议时脚本会将解码
后的相同码值归组并求均值；``raw`` 协议则直接对脉冲时序取平均。

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
BIT_THRESHOLD_US = 1000   # spaces larger than this treated as logical 1


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


def decode_protocol_nec(pulses: List[int]) -> int | None:
    """Decode a NEC infrared sequence into an integer code."""
    if len(pulses) < 4:
        return None
    if pulses[0] < 8000 or pulses[0] > 10000:
        return None
    if pulses[1] < 4000 or pulses[1] > 5000:
        return None
    bits = []
    i = 2
    while i + 1 < len(pulses):
        pulse = pulses[i]
        space = pulses[i + 1]
        if pulse < 200:
            break
        if space > BIT_THRESHOLD_US:
            bits.append(1)
        else:
            bits.append(0)
        i += 2
    if len(bits) not in {16, 32}:
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


def average_pulses(groups: List[List[int]]) -> List[int]:
    """Average multiple pulse sequences index by index."""
    max_len = max(len(g) for g in groups)
    avg: List[int] = []
    for i in range(max_len):
        values = [g[i] for g in groups if i < len(g)]
        avg.append(round(statistics.fmean(values)))
    return avg


def build_conf_raw(
    pulses: List[int],
    name: str,
    remote: str = "myremote",
    flags: str = "RAW_CODES",
) -> str:
    """Create a minimal LIRC configuration using RAW_CODES."""
    lines = [
        "begin remote",
        f"  name  {remote}",
        f"  flags  {flags}",
        "  eps            30",
        "  aeps           100",
        f"  gap           {THRESHOLD_GAP_US}",
        "  frequency    38000",
        "",
        "  begin raw_codes",
        f"    name {name}",
        "      " + " ".join(str(p) for p in pulses),
        "  end raw_codes",
        "end remote",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 mode2 日志转换为 LIRC 配置文件")
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
        "--proto",
        choices=["nec", "raw"],
        default="nec",
        help="协议类型：nec 或 raw，默认 nec",
    )
    parser.add_argument(
        "--flags",
        default="SPACE_ENC|CONST_LENGTH",
        help="LIRC remote flags",
    )
    args = parser.parse_args()

    groups = parse_log(args.log)
    print(f"检测到 {len(groups)} 组数据")

    key_name = args.key if args.key else "KEY_1"

    if args.proto == "nec":
        codes_by_value: Dict[int, List[int]] = {}
        order: List[int] = []
        for grp in groups:
            code = decode_protocol_nec(grp)
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

        codes: List[int] = [round(statistics.fmean(codes_by_value[order[0]]))]
        key_names = [key_name]
        conf = build_conf(codes, key_names, args.name, args.flags)
    else:
        pulses = average_pulses(groups)
        conf = build_conf_raw(pulses, key_name, args.name, args.flags)

    args.output.write_text(conf)
    print(f"已写入 {args.output}")


if __name__ == "__main__":
    main()
