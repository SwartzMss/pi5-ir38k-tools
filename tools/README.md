# mode2\_to\_lirc.py

该脚本用于将 `mode2` 命令输出的日志转换为 LIRC SPACE_ENC 配置文件。

专注于兼容性最好的 **SPACE\_ENC** 格式，优先支持 **Gree 空调协议**，同时兼容其他常见红外协议。

## 协议支持

- 🥇 **Gree 空调协议**（优先支持，自动识别）
- 🥈 **NEC 协议**（通用协议，备用解码）
- 🏗️ **其他协议**（使用通用SPACE_ENC格式兼容）

## 依赖

- Python 3.10+

## 安装

```bash
git clone https://github.com/SwartzMss/pi5-ir38k-tools.git
cd pi5-ir38k-tools/tools
```

## 使用示例

```bash
# 生成 Gree 空调配置文件
python mode2_to_lirc.py \
  --log power.log \
  --key KEY_POWER \
  --name gree_remote \
  --output gree.conf
```

## 参数说明

| 参数         | 描述                        | 默认值           |
| ---------- | ------------------------- | ------------- |
| `--log`    | `mode2` 输出的原始脉冲日志文件路径     | 必填            |
| `--key`    | LIRC 配置中的键名               | `KEY_1`       |
| `--name`   | 遥控器名称                     | `myremote`    |
| `--output` | 生成的 `.conf` 文件路径          | `remote.conf` |

## 工作流程

1. **录制**：\
   运行 `mode2 > power.log`，按下遥控器按键，确保捕获完整信号。
2. **智能解码**：\
   脚本优先尝试Gree协议解码，失败时回退到NEC协议，自动分析协议参数。
3. **部署**：\
   将生成的 `.conf` 文件复制到 `/etc/lirc/lircd.conf.d/` 并重启 lircd 服务。

## SPACE_ENC 格式特点

- ✅ **兼容性好**：支持所有 LIRC 版本
- ✅ **智能解码**：优先识别Gree空调协议
- ✅ **自动检测**：智能检测协议参数（header, one, zero 等）
- ✅ **标准格式**：符合大多数红外协议标准
- ✅ **易扩展**：可轻松添加多个按键

示例输出：
```
begin remote
  name        gree_remote
  flags       SPACE_ENC|CONST_LENGTH
  bits        32
  eps         42
  aeps        44
  header      1231 448
  one         424 1269
  zero        424 452
  ptrail      424
  gap         7039
  frequency   38000

  begin codes
    KEY_POWER    0x13F
  end codes
end remote
```

## 注意事项

- 建议录制时**轻按后立即松手**，避免重复帧干扰
- 优化支持 **Gree 空调遥控器**，自动识别协议特征
- 如果信号解析失败，请检查日志文件格式是否正确
- 支持大多数常见的红外协议（Gree、NEC、Samsung等）

## 部署配置

```bash
# 复制配置文件到 LIRC 目录
sudo cp gree.conf /etc/lirc/lircd.conf.d/

# 重启 LIRC 服务
sudo systemctl restart lircd

# 检查状态
sudo systemctl status lircd

# 测试按键
irw
```

---

© 2025 SwartzMss

