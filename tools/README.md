# mode2\_to\_lirc.py

该脚本用于将 `mode2` 命令输出的日志转换为 LIRC 配置文件。

- **SPACE\_ENC** 模式（推荐，兼容性最好）
- **RAW\_CODES** 模式（原始脉冲时序，备用选项）

脚本会自动分析红外信号的协议参数，生成可直接使用的 LIRC 配置文件。

## 依赖

- Python 3.10+

## 安装

```bash
git clone https://github.com/SwartzMss/pi5-ir38k-tools.git
cd pi5-ir38k-tools/tools
```

## 使用示例

```bash
# 推荐：生成 SPACE_ENC 格式（默认）
python mode2_to_lirc.py \
  --log power.log \
  --key KEY_POWER \
  --name myremote \
  --output myremote.conf

# 备用：生成 RAW_CODES 格式
python mode2_to_lirc.py \
  --log power.log \
  --key KEY_POWER \
  --format raw \
  --output myremote.conf
```

## 参数说明

| 参数         | 描述                        | 默认值           |
| ---------- | ------------------------- | ------------- |
| `--log`    | `mode2` 输出的原始脉冲日志文件路径     | 必填            |
| `--key`    | LIRC 配置中的键名               | `KEY_1`       |
| `--name`   | 遥控器名称                     | `myremote`    |
| `--output` | 生成的 `.conf` 文件路径          | `remote.conf` |
| `--format` | 输出格式：`space_enc`(推荐) 或 `raw` | `space_enc`   |

## 工作流程

1. **录制**：\
   运行 `mode2 > power.log`，按下遥控器按键，确保捕获完整信号。
2. **转换**：\
   脚本自动分析信号协议，提取时序参数，生成配置文件。
3. **部署**：\
   将生成的 `.conf` 文件复制到 `/etc/lirc/lircd.conf.d/` 并重启 lircd 服务。

## 格式说明

### SPACE_ENC 格式（推荐）

- ✅ **兼容性好**：支持所有 LIRC 版本
- ✅ **自动解析**：智能检测协议参数（header, one, zero 等）
- ✅ **标准格式**：符合大多数红外协议标准
- ✅ **易扩展**：可轻松添加多个按键

示例输出：
```
begin remote
  name        myremote
  flags       SPACE_ENC|CONST_LENGTH
  bits        32
  eps         30
  aeps        100
  header      1231 448
  one         420 1267
  zero        420 450
  ptrail      420
  gap         7039
  frequency   38000

  begin codes
    KEY_POWER    0x40BF
  end codes
end remote
```

### RAW_CODES 格式（备用）

- ⚠️ **兼容性限制**：某些 LIRC 版本可能不支持
- ✅ **保真度高**：保留原始脉冲时序
- ⚠️ **单按键限制**：每次只能生成一个按键

## 注意事项

- 建议录制时**轻按后立即松手**，避免重复帧干扰
- 推荐使用 SPACE_ENC 格式，兼容性最好
- 如果信号解析失败，脚本会自动回退到 RAW_CODES 格式

## 部署配置

```bash
# 复制配置文件到 LIRC 目录
sudo cp myremote.conf /etc/lirc/lircd.conf.d/

# 重启 LIRC 服务
sudo systemctl restart lircd

# 检查状态
sudo systemctl status lircd

# 测试按键
irw
```

---

© 2025 SwartzMss

