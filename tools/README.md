# mode2\_to\_lirc.py

该脚本用于将 `mode2` 命令输出的日志转换为 LIRC 配置文件。

- **RAW\_CODES** 模式（直接输出脉冲时序）

无需手动设置时序参数，脚本会自动对多帧数据取平均值，生成稳定的 RAW\_CODES 格式配置。

## 依赖

- Python 3.10+

## 安装

```bash
git clone https://github.com/SwartzMss/pi5-ir38k-tools.git
cd pi5-ir38k-tools/tools
```

## 使用示例

```bash
python mode2_to_lirc.py \
  --log xxx.log \
  --key KEY_POWER \
  --name myremote \
  --output myremote.conf
```

- 直接生成 RAW\_CODES 格式配置。

## 参数说明

| 参数         | 描述                        | 默认值           |
| ---------- | ------------------------- | ------------- |
| `--log`    | `mode2` 输出的原始脉冲日志文件路径     | 必填            |
| `--key`    | LIRC 配置中的键名               | `KEY_1`       |
| `--name`   | 遥控器名称                     | `myremote`    |
| `--output` | 生成的 `.conf` 文件路径          | `remote.conf` |

## 工作流程

1. **录制**：\
   运行 `mode2 > logfile`，连续多次按下同一按键，确保捕获完整帧数据。
2. **转换**：\
   脚本自动对所有帧的时序数组分别按索引求平均值，输出 RAW\_CODES 格式。
3. **输出**：\
   生成的 `.conf` 即可直接在 LIRC 中使用。

## 为什么选择 RAW\_CODES 模式？

- **兼容性**：不受 64 位限制，支持任何复杂协议
- **完整性**：保留原始时序信息，无数据丢失
- **稳定性**：对多帧取平均，消除噪音影响
- **通用性**：适用于所有红外遥控器，包括空调等复杂设备

## 注意事项

- 仅支持一次解析一个按键。如日志包含多种按键，请分别录制。
- 建议录制 3-5 次按键操作，脚本会自动计算平均时序。
- 建议录制时**轻按后立即松手**，避免重复帧干扰。

---

© 2025 SwartzMss

