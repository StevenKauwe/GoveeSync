import base64
import signal
import socket
import time
from enum import Enum
from typing import Union

import numpy as np
from PIL import Image, ImageEnhance, ImageGrab
from pydantic import BaseModel, Field

DEBUG = False
UDP_PORT = 4003
MAX_LED_COLOR_GRADIENT = 10


class PowerState(Enum):
    OFF = 0
    ON = 1


class Color(BaseModel):
    r: int = Field(default=205, ge=0, le=255)
    g: int = Field(default=125, ge=0, le=255)
    b: int = Field(default=0, ge=0, le=255)

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
        if DEBUG:
            print(f"Command sent to {self.ip}: {message}")

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
        """Returns the SegmentData object for the given list of colors.

        The segment data is a base64 encoded string that represents the colors to be set.
        I have no idea what the values for the first 4 bytes are.
        I assume the 6th byte is the number of colors.
        """
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


def get_device_location_indices(
    column_indices: list[int] | None = None, row_indices: list[int] | None = None
):
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
    if column_indices is None:
        column_indices = list(range(MAX_LED_COLOR_GRADIENT))
    if row_indices is None:
        # light lamp colors are ordered from bottom to top
        row_indices = list(range(MAX_LED_COLOR_GRADIENT)[::-1])
    screen_indices = [row_indices, column_indices]
    return screen_indices


def example_usage():
    default_color = Color(r=255, g=165, b=0)
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
    # Capture the entire screen
    screen_image = ImageGrab.grab()
    resize_factor = 10

    # Resize image to a manageable size that maintains the aspect ratio of 10x10 blocks
    resized_image = screen_image.resize(
        (MAX_LED_COLOR_GRADIENT * resize_factor, MAX_LED_COLOR_GRADIENT * resize_factor)
    )

    # Increase the saturation by 1.5 times
    converter = ImageEnhance.Color(resized_image)
    saturated_image = converter.enhance(2.5)

    # Convert image to numpy array for processing
    color_matrix = np.array(saturated_image)

    # Reshape the array to (10, 10, 10, 10, 3) where each 10x10 block's pixels are separately accessible
    color_matrix = color_matrix.reshape(
        (
            MAX_LED_COLOR_GRADIENT,
            resize_factor,
            MAX_LED_COLOR_GRADIENT,
            resize_factor,
            3,
        )
    )

    # I favor red > green > blue for the most "colorful pixel". Let's scale the colors accordingly
    biased_color_matrix = color_matrix.copy()
    biased_color_matrix[..., 0] *= 2
    biased_color_matrix[..., 1] *= 1
    biased_color_matrix[..., 2] *= 1

    # Compute variance across each pixel to find the most "colorful" pixel
    pixel_variances = np.var(biased_color_matrix, axis=4)

    # Transpose the array so that the 10x10 blocks are along the last two axes
    pixel_variances_transposed = pixel_variances.transpose(0, 2, 1, 3)

    # Flatten the last two dimensions
    pixel_variances_flattened = pixel_variances_transposed.reshape(
        MAX_LED_COLOR_GRADIENT, MAX_LED_COLOR_GRADIENT, -1
    )

    # Compute argmax over the flattened dimension
    max_colorful_indices = np.unravel_index(
        pixel_variances_flattened.argmax(axis=2), (resize_factor, resize_factor)
    )

    # For each block, get the most colorful pixel
    most_colorful_pixels = color_matrix[
        np.arange(MAX_LED_COLOR_GRADIENT)[:, None],
        max_colorful_indices[0],
        np.arange(MAX_LED_COLOR_GRADIENT),
        max_colorful_indices[1],
    ]

    most_colorful_pixels = most_colorful_pixels.reshape(
        MAX_LED_COLOR_GRADIENT, MAX_LED_COLOR_GRADIENT, 3
    )

    if DEBUG:
        saturated_image.save("debug_saturated_image.png")

        most_colorful_pixels_image = Image.fromarray(
            most_colorful_pixels.astype(np.uint8), "RGB"
        )
        most_colorful_pixels_image.save("debug_preview.png")
        # raise an exception to stop the program and show the image
        raise Exception("Debug mode enabled. Stopping program to show image.")

    return most_colorful_pixels


class FrameCounter:
    def __init__(self):
        self.last_100_fps = []
        self.start_time = time.time()
        self.previous_time = time.time()

    def update_and_print(self):
        elapsed_time = time.time() - self.previous_time
        self.previous_time = time.time()
        time_since_start = time.time() - self.start_time
        fps = 1 / elapsed_time
        self.last_100_fps = self.last_100_fps[-99:]
        self.last_100_fps.append(fps)
        average_fps = (
            sum(self.last_100_fps) / len(self.last_100_fps) if self.last_100_fps else 0
        )
        print(
            f"\rFPS: {fps:.1f} - Average FPS {average_fps:.1f} - Total Time:{time_since_start:.1f}",
            end="",
        )

        return fps

    def reset(self):
        self.frame_count = 0
        self.start_time = time.time()


def game_loop(devices: list[GoveeLightDevice]):
    frame_counter = FrameCounter()
    try:
        for device in devices:
            device.power_on()
            time.sleep(0.1)
            device.set_brightness(100)
            time.sleep(0.1)
            device.set_color(Color())

        time.sleep(0.5)

        for device in devices:
            device.initialize_segment()

        while True:
            screen_colors = capture_screen_and_process_colors()
            for device in devices:
                selected_rows = screen_colors[device.screen_positions[0], :, :]
                selected_columns = selected_rows[:, device.screen_positions[1], :]
                color_data = [
                    Color(r=r, g=g, b=b)
                    for r, g, b in selected_columns.mean(axis=1).astype(int)
                ]
                device.set_segment_colors(color_data)
            frame_counter.update_and_print()
            # write to terminal a fps counter (but don't print it every frame, instead update it in place)

    except KeyboardInterrupt:
        print("Operation stopped by user.")
    finally:
        for device in devices:
            device.terminate_segment()
            time.sleep(0.5)
            device.power_off()


def run():
    left_column_device = GoveeLightDevice(
        "192.168.0.248", "Govee Light Right", get_device_location_indices([7, 8, 9])
    )
    right_column_device = GoveeLightDevice(
        "192.168.0.108",
        "Govee Light Left",
        get_device_location_indices([0, 1, 2]),
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
