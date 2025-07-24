"""示例代码：在 Raspberry Pi 5 上发送和接收 38kHz 红外信号。"""

from ir_device import IRSender, IRReceiver

TX_PIN = 18  # 红外 LED 所在的 GPIO
RX_PIN = 23  # 红外接收头所在的 GPIO


def main():
    sender = IRSender(TX_PIN)
    receiver = IRReceiver(RX_PIN)
    try:
        print("发送 38kHz 脉冲...")
        sender.send_pulse()
        print("等待信号...")
        if receiver.wait():
            print("检测到红外信号")
        else:
            print("未检测到红外信号")
    finally:
        sender.close()
        receiver.close()


if __name__ == "__main__":
    main()
