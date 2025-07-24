"""示例代码：在 Raspberry Pi 5 上发送和接收 38kHz 红外信号。"""

import time
import lgpio

TX_PIN = 18  # 红外 LED 所在的 GPIO
RX_PIN = 23  # 红外接收头所在的 GPIO


def send_pulse(handle, duration=0.5, freq=38000, duty_cycle=0.5):
    """发送指定持续时间的 38kHz 红外载波信号。"""
    duty = int(duty_cycle * 1_000_000)  # 占空比分子, 范围 0-1_000_000
    lgpio.tx_pwm(handle, TX_PIN, freq, duty)
    time.sleep(duration)
    lgpio.tx_pwm(handle, TX_PIN, 0, 0)


def wait_signal(handle, timeout=5):
    """等待红外信号，超时时间单位为秒。"""
    start = time.time()
    while time.time() - start < timeout:
        if lgpio.gpio_read(handle, RX_PIN):
            print("检测到红外信号")
            return True
        time.sleep(0.01)
    print("未检测到红外信号")
    return False


def main():
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_output(h, TX_PIN)
    lgpio.gpio_claim_input(h, RX_PIN)
    try:
        print("发送 38kHz 脉冲...")
        send_pulse(h)
        print("等待信号...")
        wait_signal(h)
    finally:
        lgpio.gpiochip_close(h)


if __name__ == "__main__":
    main()
