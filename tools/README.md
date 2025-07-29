# mode2_to_lirc.py

该脚本用于将 `mode2` 命令输出的日志转换为 LIRC 配置文件。默认按 **NEC 协议** 解码并生成 ENC 格式，也可以通过 `--proto raw` 直接输出 `RAW_CODES`。需要 Python 3.10 及以上。预留了 `decode_protocol_rc5`、`decode_protocol_sony` 两个空钩子，便于后续扩展其他协议。

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
- `--proto`：协议类型，可选 `nec` 或 `raw`，默认为 `nec`。

如未解析到有效码值或检测到多个不同码值，脚本会报错并显示帮助信息。

录制时建议**轻按后立即松手**，避免 NEC 重复帧干扰。

脚本会打印检测到的组数，NEC 模式下会解析码值并求平均；RAW 模式则直接对脉冲
取平均。最终生成的配置文件可直接用于 LIRC，其中 NEC 模式的码值以 `0x` 开头的
十六进制表示。
