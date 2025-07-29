"""将 mode2 日志转换为 LIRC SPACE_ENC 配置文件。

专注于兼容性最好的 SPACE_ENC 格式，自动分析协议参数。
Requires Python 3.10+

Usage:
  python mode2_to_lirc.py --log key.log --key KEY_POWER \
      --output myremote.conf --name myremote
"""
import argparse
import logging
import statistics
from pathlib import Path
from typing import Dict, List, Literal, Union, Optional

# Constants
THRESHOLD_GAP_US = 8000   # 长空间阈值，用于分隔帧
BIT_THRESHOLD_US = 1000    # 默认位空间阈值

# NEC 重复帧标记
NEC_REPEAT = "__repeat__"

# 日志配置
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_log(path: Path) -> List[List[int]]:
    """流式读取 mode2 日志，返回脉冲/空间序列列表（按帧分组）。"""
    if not path.exists():
        raise FileNotFoundError(f"日志文件不存在: {path}")
    
    groups: List[List[int]] = []
    current: List[int] = []
    line_count = 0
    valid_lines = 0
    timeout_count = 0
    
    with path.open() as f:
        for line in f:
            line_count += 1
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            typ, raw = parts
            
            # 处理 timeout 行作为帧分隔符
            if typ == "timeout":
                timeout_count += 1
                if current:
                    groups.append(current)
                    current = []
                continue
                
            if typ not in {"pulse", "space"}:
                continue
            try:
                val = int(raw)
                valid_lines += 1
            except ValueError:
                continue
            # 长空间视为帧分隔符（备用方案）
            if typ == "space" and val > THRESHOLD_GAP_US and current:
                groups.append(current)
                current = []
                continue
            current.append(val)
    if current:
        groups.append(current)
    
    logger.info(f"读取了 {line_count} 行，有效数据 {valid_lines} 行，检测到 {timeout_count} 个timeout，检测到 {len(groups)} 帧")
    
    # 添加帧长度调试信息
    if groups:
        lengths = [len(g) for g in groups]
        logger.info(f"帧长度分布: {lengths}")
        if len(set(lengths)) > 1:
            logger.warning(f"检测到不同长度的帧: {set(lengths)}")
    
    return groups


def auto_detect_params(frames: List[List[int]]) -> Dict[str, int]:
    """根据多帧计算出 SPACE_ENC 参数字典。"""
    if not frames:
        raise RuntimeError("未检测到任何帧数据，请检查日志文件格式或阈值设置。")
    
    lengths = [len(f) for f in frames]
    try:
        target_len = statistics.mode(lengths)
    except statistics.StatisticsError:
        target_len = max(set(lengths), key=lengths.count)

    candidates = [f for f in frames if len(f) == target_len]
    if not candidates:
        raise RuntimeError("未检测到完整帧，请检查日志或阈值设置。")

    # 检查帧长度是否足够
    if target_len < 4:
        raise RuntimeError(f"帧长度过短 ({target_len})，无法解析协议参数。需要至少4个值。")

    # 对齐并取中位数
    medians = [
        int(statistics.median([frame[i] for frame in candidates]))
        for i in range(target_len)
    ]
    header_pulse, header_space = medians[0], medians[1]
    
    # 确保有足够的数据来形成脉冲-空间对
    if target_len < 4:
        raise RuntimeError("帧数据不足，无法解析协议参数")
    
    pairs = [(medians[i], medians[i+1]) for i in range(2, target_len-1, 2)]
    if not pairs:
        raise RuntimeError("无法从帧数据中提取脉冲-空间对")
        
    data_pulses = [p for p, _ in pairs]
    bit_spaces = [s for _, s in pairs]

    sorted_spaces = sorted(bit_spaces)
    mid = len(sorted_spaces) // 2
    zero_space = int(statistics.median(sorted_spaces[:mid])) if mid else 0
    one_space = int(statistics.median(sorted_spaces[mid:])) if sorted_spaces[mid:] else 0
    bit_th = (zero_space + one_space) // 2 if zero_space and one_space else BIT_THRESHOLD_US

    eps = max(5, int(statistics.median(data_pulses) * 0.1))
    aeps = max(20, int(header_space * 0.1))
    gap_candidates = [s for s in bit_spaces if s > one_space * 1.5]
    gap = int(statistics.median(gap_candidates)) if gap_candidates else THRESHOLD_GAP_US
    bits = len(pairs)

    # 对于Gree协议，保持检测到的真实位数
    logger.info(f"检测到 {bits} 个数据对，保持原始位数")

    return {
        "header_pulse": header_pulse,
        "header_space": header_space,
        "bit_pulse": int(statistics.median(data_pulses)),
        "zero_space": zero_space,
        "one_space": one_space,
        "bit_th": bit_th,
        "gap": gap,
        "eps": eps,
        "aeps": aeps,
        "bits": bits,  # 使用真实检测到的位数
    }


def decode_protocol_nec(
    pulses: List[int],
    stats: Dict[str, int],
    supported_lengths: List[int]
) -> Union[int, Literal[NEC_REPEAT], None]:
    """Decode NEC 脉冲序列至码值或标记，失败返回 None。"""
    if len(pulses) < 3:
        return None
    # 校验帧头
    if not (stats["header_pulse"] * 0.9 <= pulses[0] <= stats["header_pulse"] * 1.1 and
            stats["header_space"] * 0.9 <= pulses[1] <= stats["header_space"] * 1.1):
        return None
    # 重复帧
    if len(pulses) <= 4 and pulses[2] < 700:
        return NEC_REPEAT

    bits: List[int] = []
    i = 2
    while i + 1 < len(pulses):
        pulse, space = pulses[i], pulses[i+1]
        if pulse < 200:
            break
        bits.append(1 if space > stats["bit_th"] else 0)
        i += 2
    if len(bits) not in supported_lengths:
        return None

    value = 0
    for b in bits:
        value = (value << 1) | b
    return value


def decode_protocol_gree(
    pulses: List[int],
    stats: Optional[Dict[str, int]] = None
) -> Optional[int]:
    """Decode Gree 空调协议：返回完整帧（35+32 bit）组合成的整数，失败返回 None。"""
    # 使用 auto_detect_params 生成 stats 时，stats['bits'] 应等于总 bit 数
    # 检测帧头
    if len(pulses) < 4:
        return None
    hp, hs = pulses[0], pulses[1]
    # 基于 auto_detect_params 头部统计范围
    if stats and not (stats["header_pulse"] * 0.9 <= hp <= stats["header_pulse"] * 1.1 and
                      stats["header_space"] * 0.9 <= hs <= stats["header_space"] * 1.1):
        return None
    # 解析所有位：跳过任何跨块大间隙
    bits: List[int] = []
    i = 2
    gap_th = stats["gap"] if stats else THRESHOLD_GAP_US
    bit_th = stats["bit_th"] if stats else BIT_THRESHOLD_US
    while i + 1 < len(pulses):
        pulse, space = pulses[i], pulses[i+1]
        # 跨块分隔或尾部
        if space > gap_th:
            i += 2
            continue
        if pulse < 200:
            break
        bits.append(1 if space > bit_th else 0)
        i += 2
    if not bits:
        return None
    # 合并所有位到单个整数
    value = 0
    for b in bits:
        value = (value << 1) | b
    return value


def build_conf_space_enc(
    code: int,
    name: str,
    cfg: Dict[str, int],
    remote: str
) -> str:
    """生成 SPACE_ENC 格式的 LIRC 配置文本（CONST_LENGTH模式，适用于Gree等复杂协议）。"""
    
    lines = [
        "begin remote",
        f"  name        {remote}",
        f"  flags       SPACE_ENC|CONST_LENGTH",
        f"  bits        {cfg['bits']}",
        f"  eps         30",
        f"  aeps        100",
        f"  header      {cfg['header_pulse']} {cfg['header_space']}",
        f"  one         0 0",
        f"  zero        0 0",
        f"  gap         {cfg['gap']}",
        f"  toggle_bit_mask 0x0",
        f"  frequency   38000",
        "",
        "  begin codes",
        f"    {name:<16} 0x{code:X}",
        "  end codes",
        "end remote"
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 mode2 日志转换为 LIRC SPACE_ENC 配置文件",
        epilog="专注于兼容性最好的 SPACE_ENC 格式"
    )
    parser.add_argument("--log", type=Path, required=True, help="mode2 输出的日志文件路径")
    parser.add_argument("--key", default="KEY_1", help="按键名称，默认 KEY_1")
    parser.add_argument("-o", "--output", type=Path, default=Path("remote.conf"), help="输出 conf 文件路径")
    parser.add_argument("--name", default="myremote", help="遥控器名称，默认 myremote")
    args = parser.parse_args()

    try:
        frames = parse_log(args.log)
    except FileNotFoundError as e:
        parser.error(str(e))
    except Exception as e:
        parser.error(f"解析日志文件时出错: {e}")

    logger.info(f"检测到 {len(frames)} 帧数据")

    if not frames:
        parser.error("未检测到任何帧数据，请检查日志文件格式或阈值设置。")

    # 选择第一个完整帧，而不是多帧平均
    first_frame = frames[0]
    logger.info(f"使用第一帧数据，长度: {len(first_frame)} 个值")
    
    # 移除帧间隙（大于gap阈值的space值）
    # SPACE_ENC 需要完整的第一帧用于参数检测
    clean_frame = []
    
    # 新策略：寻找第一个完整的脉冲序列
    # 通常一个完整的红外帧应该有合理的长度（比如50-100个值）
    # 在遇到第一个大间隙(>6000μs)时，检查是否已有足够数据构成完整帧
    min_frame_length = 20  # 最小帧长度
    
    for i, value in enumerate(first_frame):
        # 如果是space（奇数索引）且大于6000μs，且已有足够的数据，停止
        if (i % 2 == 1 and value > 6000 and len(clean_frame) >= min_frame_length):
            logger.info(f"检测到大间隙 {value}μs，在位置 {i+1}，已收集 {len(clean_frame)} 个值，停止")
            break
            
        clean_frame.append(value)
    
    # 验证数据完整性
    if len(clean_frame) < 4:
        parser.error(f"清理后的脉冲数据过短 ({len(clean_frame)} 个值)，无法生成有效的红外信号")
    
    logger.info(f"清理后脉冲数据长度: {len(clean_frame)} 个值")
    if len(clean_frame) % 2 != 0:
        logger.warning("脉冲数据个数为奇数，将自动修正为偶数个")
    
    # 生成 SPACE_ENC 格式配置
    try:
        cfg = auto_detect_params(frames)
        # 优先尝试解码Gree空调协议
        code = decode_protocol_gree(clean_frame, cfg)
        if code is not None:
            logger.info(f"成功使用Gree协议解码按键值: 0x{code:X}")
        else:
            # 如果Gree解码失败，尝试NEC协议
            code = decode_protocol_nec(clean_frame, cfg, [32, 16, 24])
            if code is None:
                logger.warning("Gree和NEC协议解码都失败，使用默认值 0x40BF")
                code = 0x40BF
            elif code == NEC_REPEAT:
                logger.warning("检测到重复帧，使用默认值 0x40BF") 
                code = 0x40BF
            else:
                logger.info(f"使用NEC协议解码按键值: 0x{code:X}")
        
        content = build_conf_space_enc(code, args.key, cfg, args.name)
    except Exception as e:
        logger.error(f"SPACE_ENC 格式生成失败: {e}")
        parser.error("配置文件生成失败，请检查日志文件格式")

    args.output.write_text(content)
    logger.info(f"SPACE_ENC 配置已写入 {args.output}")

if __name__ == "__main__":
    main()
