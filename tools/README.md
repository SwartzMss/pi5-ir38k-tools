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

## RAW_CODES 格式问题与解决方案

### 常见问题

在使用生成的 RAW_CODES 配置文件时，可能遇到以下 LIRC 错误：

```
Error: bad signal length
Error: error in configfile line XX
Warning: config file contains no valid remote control definition
```

### 问题原因

1. **多帧混合**：RAW_CODES 中每个按键只能包含单帧数据，不能包含多次按键的数据
2. **包含帧间隙**：7000+μs 的大间隙值是帧分隔符，不应出现在 RAW_CODES 数据中
3. **格式不正确**：缩进和语法必须严格符合 LIRC 官方标准
4. **数据长度异常**：过长或过短的数据可能导致解析失败

### 解决方案

脚本已实现以下修复机制：

- ✅ **单帧提取**：只输出第一个完整帧的数据
- ✅ **间隙过滤**：智能检测并移除大于 6000μs 的间隙值
- ✅ **格式标准化**：严格按照 LIRC 官方文档格式输出
- ✅ **数据验证**：确保偶数个值（pulse-space 对）

### 测试配置文件

目录中提供了多个测试配置文件用于验证 LIRC 兼容性：

- `test1_minimal.conf` - 极简格式（8个值）
- `test2_standard.conf` - 标准 NEC 协议格式
- `test3_medium.conf` - 中等长度（24个值）
- `test4_different.conf` - 不同缩进格式测试
- `test5_space_enc.conf` - 传统 SPACE_ENC 格式对比

### 测试方法

```bash
# 复制测试配置到 LIRC 目录
sudo cp test1_minimal.conf /etc/lirc/lircd.conf.d/

# 重启 LIRC 服务
sudo systemctl restart lircd

# 检查状态
sudo systemctl status lircd
```

如果所有 RAW_CODES 格式都失败，建议使用 `test5_space_enc.conf` 中的传统格式。

---

© 2025 SwartzMss

