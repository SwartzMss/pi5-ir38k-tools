# pi5-ir38k-tools

基于 Linux 内核 `gpio-ir` 驱动和 LIRC 的红外收发示例。

*录一次，永远复现*

## 硬件连接

1. 红外发射管连接 GPIO18
2. 红外接收头连接 GPIO23
3. 参考 `doc` 目录的示意图完成接线

## 软件准备

1. 在 `/boot/firmware/config.txt` 中启用覆盖：
   ```
   dtoverlay=gpio-ir,gpio_pin=23
   dtoverlay=gpio-ir-tx,gpio_pin=18
   ```
2. 安装 LIRC 工具：`sudo apt install lirc`

## 录制一次

```bash
sudo python3 ir_record.py --device /dev/lirc0 --timeout 2 > code.txt
```

## 重复回放

```bash
sudo python3 ir_play.py --device /dev/lirc0 "$(cat code.txt)"
```

`ir_record.py` 会输出逗号分隔的脉冲时长（单位：微秒）。
将结果存入文件后，可使用 `ir_play.py` 无限次重放。

## 其他脚本

- `ir_send.py`：发送固定脉冲，测试发射硬件。
- `ir_recv.py`：简单等待信号，可用于检查接收硬件。
