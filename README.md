
# 树莓派 Pi 5 红外信号收发（LIRC + Python 虚拟环境）

本教程介绍如何在 Raspberry Pi 5 上，通过 LIRC 驱动和 Python 虚拟环境，**接收并发射红外遥控器信号**，为后续自动化或自定义开发打下基础。

---

## 1. 硬件准备

- 树莓派 Pi 5
- 红外接收头（如 VS1838B）
- 红外发射管
- 面包板、杜邦线

### 1.1 接线示意

| 组件     | 引脚           | 连接到 Pi 5         |
|:--------:|:--------------:|:-------------------:|
| 接收头    | OUT            | GPIO23 (BCM23)      |
| 接收头    | VCC            | 3.3V                |
| 接收头    | GND            | GND                 |
| 发射管    | + 极（长脚）    | GPIO18 (BCM18)      |
| 发射管    | - 极（短脚）    | GND                 |

---

## 2. 系统层 LIRC 驱动安装与配置

### 2.1 修改配置文件，加载 overlay

```bash
sudo nano /boot/firmware/config.txt
```
添加如下行（文件末尾）：

```ini
dtoverlay=gpio-ir,gpio_pin=23
dtoverlay=gpio-ir-tx,gpio_pin=18
```

保存并退出。

### 2.2 重启树莓派

```bash
sudo reboot
```

重启后检查：

```bash
ls /dev/lirc*
# 应有 /dev/lirc0（接收），/dev/lirc1（发射）
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
> 注意：这里只需要配置接收设备，发射时用 `irsend` 或 python 绑定直接指定 `/dev/lirc1`。

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

## 5. 红外信号发射配置与代码

### 5.1 录制或编辑遥控器码表

- 使用 LIRC 工具录制遥控器码表。

```bash
irrecord -d /dev/lirc0 ~/myremote.conf
```
跟随提示按遥控器各键，保存配置文件。制完配置文件后，需要**将其拷贝到 LIRC 的配置目录**，并重启 LIRC 服务。  
这是因为 LIRC 只会自动加载 `/etc/lirc/lircd.conf` 和 `/etc/lirc/lircd.conf.d/` 目录下的码表文件，只有这样你后续在使用 `irsend` 命令或 Python 代码时，才能成功找到你自定义的遥控器名称（如 `myremote`）。如果没有完成这一步，发射时会报“找不到遥控器”相关的错误。

拷贝并重启服务命令如下：

```bash
sudo cp ~/myremote.conf /etc/lirc/lircd.conf.d/
sudo systemctl restart lircd
```

### 5.2 命令行发射测试

假设码表定义如下：
```
begin remote

  name  myremote
  ...
  begin codes
      KEY_POWER           0x00FF00FF
  end codes
end remote
```

发射红外信号（指定发射设备）:
```bash
irsend -d /dev/lirc1 SEND_ONCE myremote KEY_POWER
```

### 5.3 Python 发射示例

在虚拟环境中，使用如下代码发送遥控器按键（如 KEY_POWER）：

```python
import lirc
import time

# 注意 lirc.init 只影响接收，用发射功能可直接用 send_once
print("发送红外 KEY_POWER 信号...")
for _ in range(3):
    lirc.send_once("myremote", ["KEY_POWER"], lircd="/var/run/lirc/lircd", device="/dev/lirc1")
    time.sleep(2)
print("发射结束")
```

> 前提：`myremote.conf` 已配置好，并已加载到 lircd（见前文），KEY_POWER 为有效码表按键。

---

## 6. 常见故障与排查

- `/dev/lirc1` 不存在？  
  → 检查 overlay 配置，确认 `dtoverlay=gpio-ir-tx,gpio_pin=18` 已加，重启后再查

- `irsend` 无反应？  
  → 检查发射管接线、极性、红外管朝向和目标设备距离。部分家电需靠近才有效。

- Python 报错或发射没反应？  
  → 检查 myremote.conf 是否已加载，KEY_POWER 是否录制正确。

- KEY_POWER 没有效果？  
  → 多录几次，尝试其他按键或其他家电。

---

