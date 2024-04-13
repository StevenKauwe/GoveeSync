import base64
import signal
import socket
import time
from enum import Enum
from typing import Union

import numpy as np
from PIL import ImageEnhance, ImageGrab
from pydantic import BaseModel, Field

UDP_PORT = 4003
MAX_LED_COLOR_GRADIENT = 10
# MAX_LED_COLOR_GRADIENT = 4


class PowerState(Enum):
    OFF = 0
    ON = 1


# Pydantic Models
class Color(BaseModel):
    r: int = Field(..., ge=0, le=255)
    g: int = Field(..., ge=0, le=255)
    b: int = Field(..., ge=0, le=255)

    @property
    def rgb(self):
        return (self.r, self.g, self.b)


class PowerData(BaseModel):
    value: PowerState


class BrightnessData(BaseModel):
    value: int


class ColorData(BaseModel):
    color: Color
    colorTemInKelvin: int = 0


class SegmentData(BaseModel):
    pt: str


class Command(BaseModel):
    cmd: str
    data: Union[PowerData, BrightnessData, ColorData, SegmentData]


class Message(BaseModel):
    msg: Command


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


class GoveeLightDevice:
    def __init__(self, ip: str, name: str, screen_positions: list[tuple[int, int]]):
        self.ip = ip
        self.name = name
        self.screen_positions = screen_positions

    def _send_command(self, command: Command):
        message = Message(msg=command).model_dump_json()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.encode(), (self.ip, UDP_PORT))
        # print(f"Command sent to {ip}: {message}")

    def power_on(self):
        power_on_command = PowerCommand(data=PowerData(value=PowerState.ON))
        self._send_command(power_on_command)

    def power_off(self):
        power_off_command = PowerCommand(data=PowerData(value=PowerState.OFF))
        self._send_command(power_off_command)

    def set_color(self, color: Color):
        color_command = ColorCommand(data=ColorData(color=color))
        self._send_command(color_command)

    def set_brightness(self, brightness: int):
        brightness_command = BrightnessCommand(data=BrightnessData(value=brightness))
        self._send_command(brightness_command)

    def initialize_segment(self):
        """Initializes a segment to be set with set_segment_colors."""
        segment_command = SegmentCommand(data=SegmentData(pt="uwABsQEK"))
        self._send_command(segment_command)

    def terminate_segment(self):
        """Returns the color to the state before the segment was initialized."""
        segment_command = SegmentCommand(data=SegmentData(pt="uwABsQAL"))
        self._send_command(segment_command)

    def set_segment_colors(self, list_of_colors: list[Color], gradient=True):
        """Sets the colors of the segment to the given list of colors.
        color list of size (min 2, max 10)

        probably move "intrepolation" and "resolution" to some other place.

        colors ordering goes from bottom to top for a lamp.
        not sure about a strip.
        but probably power source to the end of the strip.
        """

        assert (
            2 <= len(list_of_colors) <= MAX_LED_COLOR_GRADIENT
        ), f"Color list must be between 1 and 10, got {len(list_of_colors)}"

        segment_color_data = self._get_segment_color_data(list_of_colors, gradient)
        segment_command = SegmentCommand(data=segment_color_data)
        self._send_command(segment_command)

    def _get_segment_color_data(
        self, list_of_colors: list[Color], gradient=True
    ) -> SegmentData:
        gradient_flag = 1 if gradient else 0
        byte_array = [187, 0, 32, 176, gradient_flag, len(list_of_colors)]

        for color in list_of_colors:
            byte_array.extend(color.rgb)

        num2 = 0
        for byte in byte_array:
            num2 ^= byte
        byte_array.append(num2)
        final_send_value = base64.b64encode(bytes(byte_array)).decode()
        return SegmentData(pt=final_send_value)


def get_column_indices(column_number: int):
    """
    screen example for MAX_LED_COLOR_GRADIENT = 10

      column numbers
      0   1   2   3   4   5   6   7   8   9
    0 x   x   x   x   x   x   x   x   x   x
    1 x   x   x   x   x   x   x   x   x   x
    2 x   x   x   x   x   x   x   x   x   x
    3 x   x   x   x   x   x   x   x   x   x
    4 x   x   x   x   x   x   x   x   x   x
    5 x   x   x   x   x   x   x   x   x   x
    6 x   x   x   x   x   x   x   x   x   x
    7 x   x   x   x   x   x   x   x   x   x
    8 x   x   x   x   x   x   x   x   x   x
    9 x   x   x   x   x   x   x   x   x   x

    My device has index 0 at the bottom, so I need to reverse the row indices.
    """
    column_indices = [column_number] * MAX_LED_COLOR_GRADIENT
    row_indices = list(range(MAX_LED_COLOR_GRADIENT))[::-1]
    screen_indices = [column_indices, row_indices]
    return screen_indices


def example_usage():
    default_color = Color(r=255, g=165, b=0)
    # controller = LightController(["192.168.0.108", "192.168.0.248"])
    left_column_screen_indices = [(0, i) for i in range(MAX_LED_COLOR_GRADIENT)]
    left_column_device = GoveeLightDevice(
        "192.168.0.248", "Govee Light Left", left_column_screen_indices
    )

    try:
        # Example usage of the PowerCommand model
        left_column_device.power_on()

        # Example usage of the ColorCommand model
        left_column_device.set_color(default_color)
        time.sleep(1)

        # Example usage of the BrightnessCommand model
        left_column_device.set_brightness(50)
        time.sleep(1)
        left_column_device.set_brightness(100)
        time.sleep(1)

        # Example usage of the SegmentCommand model
        left_column_device.initialize_segment()

        left_column_device.set_segment_colors(
            [Color(r=25, g=0, b=0), Color(r=0, g=25, b=0)],
        )
        time.sleep(3)
        left_column_device.set_segment_colors(
            [Color(r=25, g=0, b=0), Color(r=0, g=25, b=0), Color(r=0, g=0, b=25)],
        )
        time.sleep(3)

        left_column_device.terminate_segment()

    except Exception as e:
        print(e)
    finally:
        left_column_device.power_off()


def capture_screen_and_process_colors() -> np.ndarray:
    screen_image = ImageGrab.grab()
    resized_image = screen_image.resize(
        (MAX_LED_COLOR_GRADIENT, MAX_LED_COLOR_GRADIENT)
    )

    # Increase the saturation
    converter = ImageEnhance.Color(resized_image)
    saturated_image = converter.enhance(1.5)

    color_matrix = np.array(saturated_image).transpose(1, 0, 2)

    # Replace colors that are too dark
    color_sums = color_matrix.sum(axis=2)
    dark_colors = color_sums < 10
    color_matrix[dark_colors] = [10, 10, 10]

    return color_matrix


def game_loop(devices: list[GoveeLightDevice]):
    try:
        for device in devices:
            device.power_on()
            time.sleep(0.1)
            device.set_brightness(100)
            time.sleep(0.1)
            device.set_color(Color(r=55, g=165, b=0))

        time.sleep(0.5)

        for device in devices:
            device.initialize_segment()

        while True:
            screen_colors = capture_screen_and_process_colors()
            for device in devices:
                color_data = [
                    Color(r=r, g=g, b=b)
                    for r, g, b in screen_colors[*device.screen_positions]
                ]
                device.set_segment_colors(color_data)
            time.sleep(0.005)  # 200 FPS
    except KeyboardInterrupt:
        print("Operation stopped by user.")
    finally:
        for device in devices:
            device.terminate_segment()
            time.sleep(0.5)
            device.power_off()


def run():
    left_column_device = GoveeLightDevice(
        "192.168.0.248", "Govee Light Left", get_column_indices(0)
    )
    right_column_device = GoveeLightDevice(
        "192.168.0.108",
        "Govee Light Right",
        get_column_indices(MAX_LED_COLOR_GRADIENT - 1),
    )
    devices = [left_column_device, right_column_device]

    def power_off_devices_and_exit():
        if left_column_device is not None:
            left_column_device.power_off()
        if right_column_device is not None:
            right_column_device.power_off()
        exit()

    print("Starting Govee Light Controller...")
    signal.signal(signal.SIGTERM, lambda signum, frame: power_off_devices_and_exit())
    signal.signal(signal.SIGINT, lambda signum, frame: power_off_devices_and_exit())
    game_loop(devices=devices)


if __name__ == "__main__":
    run()
