# mode2_to_lirc.py

该脚本用于将 `mode2` 命令输出的日志转换为 LIRC 配置文件（ENC 编码）。
当前实现了解码函数 `decode_protocol_nec`，仅支持 **NEC 协议**，需要 Python 3.10 及以上。预留了 `decode_protocol_rc5`、`decode_protocol_sony` 两个空钩子，便于后续扩展其他协议。

脚本一次只解析 **一个按键**，录制时请连续多次按下同一按键，以便计算平均值。

```bash
python tools/mode2_to_lirc.py --log xxx.log --key KEY_UP \
    --output myremote.conf --name myremote
```

参数说明：

- `--log`：通过 `mode2 > LOGFILE` 保存的原始脉冲数据。
- `--key`：指定按键名称，默认为 `KEY_1`。
- `-o`：输出的 `.conf` 文件路径，默认为 `remote.conf`。
- `--name`：生成的遥控器名称，默认为 `myremote`。

如未解析到有效码值或检测到多个不同码值，脚本会报错并显示帮助信息。

录制时建议**轻按后立即松手**，避免 NEC 重复帧干扰。

脚本会自动解析日志中的红外码值，按解码结果去重并求平均，
运行时会打印检测到的组数以及警告信息，
最终生成可直接用于 LIRC 的配置文件，
生成的码值以 `0x` 开头的十六进制表示，不固定位数。
