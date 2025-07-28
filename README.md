
# 树莓派 Pi 5 红外信号接收（LIRC + Python 虚拟环境）

本教程介绍如何在 Raspberry Pi 5 上，通过 LIRC 驱动和 Python 虚拟环境，**接收并识别红外遥控器信号**，为后续自动化或自定义开发打下基础。

---

## 1. 硬件准备

- 树莓派 Pi 5
- 红外接收头（如 VS1838B）
- 面包板、杜邦线
  
### 1.1 接线示意

| 红外接收头引脚 | 连接到 Pi 5  |
|:------------:|:------------:|
| OUT          | GPIO23 (BCM23)|
| VCC          | 3.3V         |
| GND          | GND          |

> 建议：OUT 同时接一个 10KΩ 电阻下拉到 GND，可减少误触发

---

## 2. 系统层 LIRC 驱动安装与配置

### 2.1 修改配置文件，加载 overlay

```bash
sudo nano /boot/firmware/config.txt
```
添加如下行（文件末尾）：

```ini
dtoverlay=gpio-ir,gpio_pin=23
```

保存并退出。

### 2.2 重启树莓派

```bash
sudo reboot
```

重启后检查：

```bash
ls /dev/lirc*
# 应有 /dev/lirc0
```

---

### 2.3 安装 LIRC 服务

（必须在系统环境执行，不涉及 venv）

```bash
sudo apt update
sudo apt install lirc
```

---

### 2.4 配置 LIRC 选项

```bash
sudo nano /etc/lirc/lirc_options.conf
```

确保如下内容：

```
driver = default
device = /dev/lirc0
```

---

### 2.5 启动并检查 LIRC 服务

```bash
sudo systemctl enable lircd
sudo systemctl restart lircd
sudo systemctl status lircd
# 确认状态为 active (running)
```

---

## 3. Python 虚拟环境配置（venv 方式）

### 3.1 创建并激活虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.2 安装 Python LIRC 绑定

```bash
pip install python-lirc
```

---

## 4. 红外信号接收与测试

### 4.1 直接用 LIRC 命令行监听（建议先这样排查）

```bash
irw
```
对准红外接收头，按下遥控器任意键，应该终端会有如下输出：

```
0000000000fd00ff 00 KEY_POWER myremote
```

如有输出，说明系统已能正确接收红外信号。

---

### 4.2 Python 示例代码：监听红外按键信号

以下代码将在虚拟环境中运行，**自动监听红外遥控器按键**：

```python
import lirc
import time

# 初始化 LIRC
sockid = lirc.init("my_lirc_app", blocking=False, lircd="/var/run/lirc/lircd")

print("正在监听红外遥控器按键... 按 Ctrl+C 退出")
try:
    while True:
        codes = lirc.nextcode()  # 获取最新的码值（如有）
        if codes:
            print("接收到红外按键:", codes)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    lirc.deinit()
    print("退出监听")
```

> ⚠️ 默认只有已经录制/配置过的遥控器码表才会输出按键名称，否则只会收到原始数据。

---

## 5. 常见故障与排查

- `/dev/lirc0` 不存在？  
  → 检查 overlay 配置、接线、重启是否到位

- `irw` 没反应？  
  → 检查红外头引脚、下拉电阻、遥控器电池

- Python 报错找不到 lirc？  
  → 确认已激活虚拟环境，并已安装 `python-lirc`

- 输出内容乱码或总是同一个？  
  → 遥控器协议未适配，多换几种遥控器或尝试录制码表

---

## 6. 后续拓展

- 录制遥控器码表，做协议识别
- 用 Python 自动执行不同操作
- 与 Home Assistant、Node-RED 等集成

---

**发射功能请见后续文档！**
