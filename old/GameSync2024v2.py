import base64
import time
from enum import Enum
from typing import List, Tuple

from PIL import ImageGrab
from pydantic import BaseModel, Field

# Configuration Constants
DEVICE_IP = ["10.1.1.54", "10.1.1.43"]
DEVICE_IP: list[str] = ["192.168.0.108", "192.168.0.248"]
UDP_PORT = 4003
NUM_COLORS = 20


# Enums for Power State
class PowerState(Enum):
    OFF = 0
    ON = 1


# Pydantic Models
class Color(BaseModel):
    r: int = Field(..., ge=0, le=255)
    g: int = Field(..., ge=0, le=255)
    b: int = Field(..., ge=0, le=255)


class Command(BaseModel):
    cmd: str
    data: BaseModel


class PowerData(BaseModel):
    value: PowerState


class BrightnessData(BaseModel):
    value: int


class ColorData(BaseModel):
    color: Color
    colorTemInKelvin: int = 0


class SegmentData(BaseModel):
    pt: str


class PowerCommand(Command):
    cmd: str = "turn"
    data: PowerData


class BrightnessCommand(Command):
    cmd: str = "brightness"
    data: BrightnessData


class ColorCommand(Command):
    cmd: str = "colorwc"
    data: ColorData


class SegmentCommand(Command):
    cmd: str = "razer"
    data: SegmentData


# Utility Functions
def capture_screen_and_process_colors(
    num_devices: int,
) -> List[List[Tuple[int, int, int]]]:
    screen_image = ImageGrab.grab()
    screen_width, screen_height = screen_image.size
    vertical_positions = [
        int(screen_height * i / NUM_COLORS) for i in range(NUM_COLORS)
    ]
    horizontal_sections = [
        int(screen_width * (i + 1) / (num_devices + 1)) for i in range(num_devices)
    ]
    return [
        [screen_image.getpixel((x, y)) for y in vertical_positions]
        for x in horizontal_sections
    ]


def format_and_send_colors(
    controller: LightController, colors: List[List[Tuple[int, int, int]]]
):
    for ip, colors_list in zip(controller.ips, colors):
        byteArray = [187, 0, 32, 176, 1, NUM_COLORS] + [
            c for color in colors_list for c in color
        ]
        checksum = sum(byteArray) % 256
        byteArray.append(checksum)
        encoded_data = base64.b64encode(bytes(byteArray)).decode()
        segment_data = SegmentData(pt=encoded_data)
        command = SegmentCommand(data=segment_data)
        controller.send_command(command)


def game_loop(controller: LightController):
    try:
        for ip in controller.ips:
            controller.send_command(PowerCommand(data=PowerData(value=PowerState.ON)))
            controller.send_command(BrightnessCommand(data=BrightnessData(value=100)))
            controller.send_command(SegmentCommand(data=SegmentData(pt="uwABsQEK")))
        time.sleep(2)

        while True:
            color_data = capture_screen_and_process_colors(len(controller.ips))
            format_and_send_colors(controller, color_data)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Operation stopped by user.")
    finally:
        for ip in controller.ips:
            controller.send_command(
                ColorCommand(
                    data=ColorData(color=Color(r=255, g=165, b=0), colorTemInKelvin=0)
                )
            )
        time.sleep(2)
        for ip in controller.ips:
            controller.send_command(SegmentCommand(data=SegmentData(pt="uwABsQAL")))
            controller.send_command(PowerCommand(data=PowerData(value=PowerState.OFF)))


def main():
    controller = LightController(DEVICE_IP)
    print("Press Ctrl+C to quit.")
    game_loop(controller)


if __name__ == "__main__":
    main()
