# mode2\_to\_lirc.py

该脚本用于将 `mode2` 命令输出的日志转换为 LIRC 配置文件。支持多种协议：

- **NEC 协议**（32bit/16bit）
- **格力空调自定义协议**（Gree）
- **RAW\_CODES** 模式（直接输出脉冲时序）

无需手动设置 `bits` 或 `flags`，脚本会自动检测：帧头、位宽、`eps`、`aeps`、`gap` 等时序参数。

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
  --output myremote.conf \
  --proto [nec|gree|raw]
```

- `--proto nec`：按 NEC 协议解码，生成 SPACE\_ENC 格式。
- `--proto gree`：按格力空调协议解码，生成 SPACE\_ENC 格式。
- `--proto raw`：对时序取平均，生成 RAW\_CODES 格式。

## 参数说明

| 参数         | 描述                        | 默认值           |
| ---------- | ------------------------- | ------------- |
| `--log`    | `mode2` 输出的原始脉冲日志文件路径     | 必填            |
| `--key`    | LIRC 配置中的键名               | `KEY_1`       |
| `--name`   | 遥控器名称                     | `myremote`    |
| `--output` | 生成的 `.conf` 文件路径          | `remote.conf` |
| `--proto`  | 协议类型：`nec`, `gree`, `raw` | `nec`         |

## 工作流程

1. **录制**：\
   运行 `mode2 > logfile`，连续多次按下同一按键，确保捕获完整帧头和数据。
2. **转换**：\
   根据 `--proto` 指定的协议类型，脚本自动解析并求平均：
   - **NEC/Gree**：按帧统计码值，去重并求中位数，输出 SPACE\_ENC。
   - **RAW**：对所有帧的时序数组分别按索引平均，输出 RAW\_CODES。
3. **输出**：\
   生成的 `.conf` 即可直接在 LIRC 中使用。

## 注意事项

- 仅支持一次解析一个按键。如日志包含多种按键，请分别录制。
- 若未解析到任何有效码或检测到多个不同码值，脚本会报错并退出。
- 建议录制时**轻按后立即松手**，避免 NEC 重复帧干扰。

---

© 2025 SwartzMss

