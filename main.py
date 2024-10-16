import subprocess
import os
import time
from paddleocr import PaddleOCR, draw_ocr

from PIL import Image

def get_connected_devices():
    """获取所有连接的设备 ID"""
    devices_output = subprocess.check_output(["adb", "devices"], universal_newlines=True)
    lines = devices_output.splitlines()[1:]  # 跳过表头
    devices = [line.split("\t")[0] for line in lines if "\tdevice" in line]
    return devices


def connect_device(ip_address, port):
    """连接指定的设备"""
    address = f"{ip_address}:{port}"
    try:
        subprocess.run(["adb", "connect", address], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"连接失败: {e.stderr}")


def take_screenshot(device_id=None):
    screenshot_dir = "./screenshot"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)

    timestamp = int(time.time())
    filename = f"{timestamp}.png"
    filepath = os.path.join(screenshot_dir, filename)
    filepath = os.path.join(screenshot_dir, filename)

    if device_id is None:
        devices = get_connected_devices()
        if not devices:
            raise RuntimeError("没有连接的设备")
        device_id = devices[0]

    try:
        subprocess.run(["adb", "-s", device_id, "shell", "screencap", "-p", "/sdcard/screenshot.png"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"截图失败: {e.stderr}")

    try:
        subprocess.run(["adb", "-s", device_id, "pull", "/sdcard/screenshot.png", filepath], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"拉取截图失败: {e.stderr}")
    return cut_screen_shot(filepath, 300, 400, 450, 240)


def cut_screen_shot(filepath, x, y, width, height):
    image = Image.open(filepath)
    cropped_image = image.crop((x, y, x + width, y + height))
    cropped_image.save(filepath)
    print(f"截图已裁剪并保存到 {filepath}")
    return filepath


def scan_question(ocr, filepath):
    result = ocr.ocr(filepath, cls=True)
    integers = []
    for item in result:
        if isinstance(item, list) and len(item) >= 2 and isinstance(item[-1], tuple):
            char = item[-1][0]
            if char.isdigit():
                integers.append(int(char))
    return integers

def main():
    filepath = ""
    ip_address = "127.0.0.1"
    port = "5575"

    connect_device(ip_address, port)
    ocr = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=True, det_model_dir=os.environ["DET_MODEL_DIR"])

    try:
        filepath = take_screenshot()
    except Exception as e:
        print(f"发生错误: {str(e)}")
    question = scan_question(ocr, filepath)

if __name__ == "__main__":
    main()